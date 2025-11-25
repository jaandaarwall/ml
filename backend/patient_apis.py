from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_security import auth_token_required, roles_required, current_user
from .Sqldatabase import db
from .models import *
from .tasks import export_patient_csv
from datetime import datetime, timedelta
from .cache import cache

class PatientDashboardAPI(Resource):
    @auth_token_required
    @roles_required('user')
    # Short cache for dashboard, invalidated by time (30s) as appointments change
    @cache.cached(timeout=30, key_prefix=lambda: f'patient_dashboard_{current_user.id}')
    def get(self):
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        
        if not patient:
            patient = Patient(user_id=current_user.id)
            db.session.add(patient)
            db.session.commit()
        
        upcoming_appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.appointment_date >= datetime.now().date(),
            Appointment.status == 'Booked'
        ).order_by(Appointment.appointment_date).all()
        
        past_appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.status == 'Completed'
        ).order_by(Appointment.appointment_date.desc()).limit(5).all()
        
        upcoming_list = []
        for apt in upcoming_appointments:
            upcoming_list.append({
                'id': apt.id,
                'doctor_name': apt.doctor.user.username,
                'department': apt.doctor.department.name,
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'time': apt.appointment_time.strftime('%H:%M'),
                'status': apt.status
            })
        
        past_list = []
        for apt in past_appointments:
            past_list.append({
                'id': apt.id,
                'doctor_name': apt.doctor.user.username,
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'status': apt.status
            })
        
        return make_response(jsonify({
            'upcoming_appointments': upcoming_list,
            'past_appointments': past_list
        }), 200)

class PatientDoctorsAPI(Resource):
    @auth_token_required
    @roles_required('user')
    # Cache for 5 minutes. Uses query string (department_id) to create distinct keys.
    @cache.cached(timeout=300, query_string=True)
    def get(self):
        department_id = request.args.get('department_id')
        
        query = Doctor.query.filter_by(is_active=True)
        
        if department_id:
            query = query.filter_by(department_id=department_id)
        
        doctors = query.all()
        
        doctors_list = []
        for doc in doctors:
            doctors_list.append({
                'id': doc.id,
                'name': doc.user.username,
                'email': doc.user.email,
                'phone': doc.user.phone,
                'department': doc.department.name,
                'qualification': doc.qualification,
                'experience_years': doc.experience_years
            })
        
        return make_response(jsonify(doctors_list), 200)

class PatientAvailableDatesAPI(Resource):
    @auth_token_required
    @roles_required('user')
    def get(self, doctor_id):
        # Get availability for next 30 days
        today = datetime.now().date()
        end_date = today + timedelta(days=30)
        
        # Fetch all availability records for this doctor in the date range
        availabilities = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.date >= today,
            DoctorAvailability.date <= end_date,
            DoctorAvailability.is_available == True
        ).order_by(DoctorAvailability.date).all()
        
        available_dates = set()
        
        for avail in availabilities:
            # Calculate max capacity for this specific shift/availability record
            # Convert times to dummy datetime to perform subtraction
            dummy_date = datetime(2000, 1, 1).date()
            start_dt = datetime.combine(dummy_date, avail.start_time)
            end_dt = datetime.combine(dummy_date, avail.end_time)
            
            duration_mins = (end_dt - start_dt).total_seconds() / 60
            slots_count = int(duration_mins // 30)
            total_capacity = slots_count * avail.total_seats
            
            # Get count of bookings strictly within this shift's time window
            booked_count = Appointment.query.filter(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == avail.date,
                Appointment.appointment_time >= avail.start_time,
                Appointment.appointment_time < avail.end_time,
                Appointment.status == 'Booked'
            ).count()
            
            # If there is at least one seat left in the aggregate for this shift
            if booked_count < total_capacity:
                available_dates.add(avail.date.strftime('%Y-%m-%d'))
        
        # Sort the dates
        sorted_dates = sorted(list(available_dates))
                
        return make_response(jsonify(sorted_dates), 200)

class PatientDoctorAvailabilityAPI(Resource):
    @auth_token_required
    @roles_required('user')
    # Cache for 60s. Doctor availability is high-traffic but dynamic.
    @cache.cached(timeout=60, query_string=True)
    def get(self, doctor_id):
        date_str = request.args.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        availabilities = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            date=date,
            is_available=True
        ).all()
        
        slots = []
        for avail in availabilities:
            start_hour = avail.start_time.hour
            start_minute = avail.start_time.minute
            end_hour = avail.end_time.hour
            end_minute = avail.end_time.minute
            
            current_time = datetime.combine(date, avail.start_time)
            end_time = datetime.combine(date, avail.end_time)
            
            while current_time < end_time:
                slot_time = current_time.time()
                
                booked_count = Appointment.query.filter_by(
                    doctor_id=doctor_id,
                    appointment_date=date,
                    appointment_time=slot_time,
                    status='Booked'
                ).count()
                
                if booked_count < avail.total_seats:
                    slots.append({
                        'time': slot_time.strftime('%H:%M'),
                        'available': True
                    })
                
                current_time += timedelta(minutes=30)
        
        return make_response(jsonify(slots), 200)

class PatientBookAppointmentAPI(Resource):
    @auth_token_required
    @roles_required('user')
    def post(self, doctor_id):
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        
        if not patient:
            patient = Patient(user_id=current_user.id)
            db.session.add(patient)
            db.session.commit()
        
        data = request.get_json()
        
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        time = datetime.strptime(data['time'], '%H:%M').time()
        
        existing = Appointment.query.filter_by(
            doctor_id=doctor_id,
            patient_id=patient.id,
            appointment_date=date,
            status='Booked'
        ).first()
        
        if existing:
            return make_response(jsonify({'message': 'You already have an appointment on this date'}), 409)
        
        availability = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            date=date
        ).first()
        
        if not availability:
            return make_response(jsonify({'message': 'Doctor not available on this date'}), 400)
        
        booked_count = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=date,
            appointment_time=time,
            status='Booked'
        ).count()
        
        if booked_count >= availability.total_seats:
            return make_response(jsonify({'message': 'This time slot is fully booked'}), 400)
        
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            appointment_date=date,
            appointment_time=time,
            reason=data.get('reason')
        )
        
        db.session.add(appointment)
        db.session.commit()
                
        doctor = Doctor.query.get(doctor_id)
        price = doctor.department.price   # Price based on department

        payment = Payment(
            appointment_id=appointment.id,
            amount=price,
            status='Pending'
        )
        db.session.add(payment)
        db.session.commit()

        payment_link = f"http://localhost:5173/payment/{payment.id}"
        
        # Explicitly invalidate dashboard cache for this user
        cache.delete(f'patient_dashboard_{current_user.id}')

        return make_response(jsonify({
            "message": "Appointment booked successfully",
            "appointment_id": appointment.id,
            "payment_id": payment.id,
            "amount": price,
            "payment_url": payment_link
        }), 201)



class PatientAppointmentsAPI(Resource):
    @auth_token_required
    @roles_required('user')
    def get(self):
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        
        if not patient:
            return make_response(jsonify([]), 200)
        
        appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(
            Appointment.appointment_date.desc()
        ).all()
        
        appointments_list = []
        for apt in appointments:
            treatment = Treatment.query.filter_by(appointment_id=apt.id).first()
            appointments_list.append({
                'id': apt.id,
                'doctor_name': apt.doctor.user.username,
                'department': apt.doctor.department.name,
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'time': apt.appointment_time.strftime('%H:%M'),
                'status': apt.status,
                'reason': apt.reason,
                'diagnosis': treatment.diagnosis if treatment else None,
                'prescription': treatment.prescription if treatment else None,
                'notes': treatment.notes if treatment else None
            })
        
        return make_response(jsonify(appointments_list), 200)

class PatientCancelAppointmentAPI(Resource):
    @auth_token_required
    @roles_required('user')
    def post(self, appointment_id):
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        appointment = Appointment.query.get_or_404(appointment_id)
        
        if appointment.patient_id != patient.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        if appointment.status != 'Booked':
            return make_response(jsonify({'message': 'Cannot cancel this appointment'}), 400)
        
        appointment.status = 'Cancelled'
        db.session.commit()
        
        # Invalidate dashboard cache on cancellation
        cache.delete(f'patient_dashboard_{current_user.id}')
        
        return make_response(jsonify({'message': 'Appointment cancelled successfully'}), 200)

class PatientHistoryAPI(Resource):
    @auth_token_required
    @roles_required('user')
    def get(self):
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        
        if not patient:
            return make_response(jsonify([]), 200)
        
        appointments = Appointment.query.filter_by(
            patient_id=patient.id,
            status='Completed'
        ).order_by(Appointment.appointment_date.desc()).all()
        
        history = []
        for apt in appointments:
            treatment = Treatment.query.filter_by(appointment_id=apt.id).first()
            history.append({
                'id': apt.id,
                'doctor_name': apt.doctor.user.username,
                'department': apt.doctor.department.name,
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'diagnosis': treatment.diagnosis if treatment else None,
                'prescription': treatment.prescription if treatment else None,
                'notes': treatment.notes if treatment else None,
                'follow_up_required': treatment.follow_up_required if treatment else False,
                'follow_up_date': treatment.follow_up_date.strftime('%Y-%m-%d') if treatment and treatment.follow_up_date else None
            })
        
        return make_response(jsonify(history), 200)

class PatientProfileAPI(Resource):
    @auth_token_required
    @roles_required('user')
    def get(self):
        return make_response(jsonify({
            'username': current_user.username,
            'email': current_user.email,
            'phone': current_user.phone,
            'date_of_birth': current_user.date_of_birth.strftime('%Y-%m-%d') if current_user.date_of_birth else None,
            'gender': current_user.gender,
            'blood_group': current_user.blood_group,
            'address': current_user.address
        }), 200)
    
    @auth_token_required
    @roles_required('user')
    def put(self):
        from flask_security import utils
        data = request.get_json()
        
        current_user.username = data.get('username', current_user.username)
        current_user.phone = data.get('phone', current_user.phone)
        current_user.gender = data.get('gender', current_user.gender)
        current_user.blood_group = data.get('blood_group', current_user.blood_group)
        current_user.address = data.get('address', current_user.address)
        
        if data.get('date_of_birth'):
            current_user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            
        if data.get('password'):
            current_user.password = utils.hash_password(data['password'])
        
        db.session.commit()
        
        return make_response(jsonify({'message': 'Profile updated successfully'}), 200)