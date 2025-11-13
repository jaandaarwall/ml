from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_security import auth_token_required, roles_required, current_user
from .Sqldatabase import db
from .models import *
from datetime import datetime, timedelta, time as dt_time

class DoctorDashboardAPI(Resource):
    @auth_token_required
    @roles_required('doctor')
    def get(self):
        doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
        
        today = datetime.now().date()
        today_appointments = Appointment.query.filter_by(
            doctor_id=doctor.id,
            appointment_date=today
        ).all()
        
        next_week = today + timedelta(days=7)
        upcoming_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date.between(today, next_week),
            Appointment.status == 'Booked'
        ).order_by(Appointment.appointment_date).all()
        
        total_patients = db.session.query(Appointment.patient_id).filter_by(
            doctor_id=doctor.id
        ).distinct().count()
        
        today_list = []
        for apt in today_appointments:
            today_list.append({
                'id': apt.id,
                'patient_name': apt.patient.user.username,
                'time': apt.appointment_time.strftime('%H:%M'),
                'status': apt.status,
                'reason': apt.reason
            })
        
        upcoming_list = []
        for apt in upcoming_appointments:
            upcoming_list.append({
                'id': apt.id,
                'patient_name': apt.patient.user.username,
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'time': apt.appointment_time.strftime('%H:%M')
            })
        
        return make_response(jsonify({
            'today_appointments': today_list,
            'upcoming_appointments': upcoming_list,
            'total_patients': total_patients
        }), 200)

class DoctorAppointmentsAPI(Resource):
    @auth_token_required
    @roles_required('doctor')
    def get(self):
        doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
        appointments = Appointment.query.filter_by(doctor_id=doctor.id).order_by(
            Appointment.appointment_date.desc()
        ).all()
        
        appointments_list = []
        for apt in appointments:
            appointments_list.append({
                'id': apt.id,
                'patient_name': apt.patient.user.username,
                'patient_id': apt.patient_id,
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'time': apt.appointment_time.strftime('%H:%M'),
                'status': apt.status,
                'reason': apt.reason
            })
        
        return make_response(jsonify(appointments_list), 200)

class DoctorPatientsAPI(Resource):
    @auth_token_required
    @roles_required('doctor')
    def get(self):
        doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
        
        patients = db.session.query(Patient).join(Appointment).filter(
            Appointment.doctor_id == doctor.id
        ).distinct().all()
        
        patients_list = []
        for patient in patients:
            appointments_count = Appointment.query.filter_by(
                doctor_id=doctor.id,
                patient_id=patient.id
            ).count()
            
            patients_list.append({
                'id': patient.id,
                'name': patient.user.username,
                'email': patient.user.email,
                'phone': patient.user.phone,
                'blood_group': patient.user.blood_group,
                'appointments_count': appointments_count
            })
        
        return make_response(jsonify(patients_list), 200)

class DoctorAvailabilityAPI(Resource):
    @auth_token_required
    @roles_required('doctor')
    def get(self):
        doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
        availabilities = DoctorAvailability.query.filter_by(doctor_id=doctor.id).all()
        
        availability_list = []
        for avail in availabilities:
            availability_list.append({
                'id': avail.id,
                'date': avail.date.strftime('%Y-%m-%d'),
                'start_time': avail.start_time.strftime('%H:%M'),
                'end_time': avail.end_time.strftime('%H:%M'),
                'total_seats': avail.total_seats,
                'is_available': avail.is_available
            })
        
        return make_response(jsonify(availability_list), 200)
    
    @auth_token_required
    @roles_required('doctor')
    def post(self):
        doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
        data = request.get_json()
        
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        
        availability = DoctorAvailability(
            doctor_id=doctor.id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            total_seats=data.get('total_seats', 10)
        )
        
        db.session.add(availability)
        db.session.commit()
        
        return make_response(jsonify({'message': 'Availability added successfully'}), 201)
    
    @auth_token_required
    @roles_required('doctor')
    def delete(self):
        availability_id = request.args.get('id')
        availability = DoctorAvailability.query.get_or_404(availability_id)
        
        doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
        if availability.doctor_id != doctor.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        db.session.delete(availability)
        db.session.commit()
        
        return make_response(jsonify({'message': 'Availability deleted successfully'}), 200)

class DoctorCompleteAppointmentAPI(Resource):
    @auth_token_required
    @roles_required('doctor')
    def post(self, appointment_id):
        doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
        appointment = Appointment.query.get_or_404(appointment_id)
        
        if appointment.doctor_id != doctor.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        appointment.status = 'Completed'
        db.session.commit()
        
        return make_response(jsonify({'message': 'Appointment marked as completed'}), 200)

class DoctorTreatmentAPI(Resource):
    @auth_token_required
    @roles_required('doctor')
    def get(self, appointment_id):
        doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
        appointment = Appointment.query.get_or_404(appointment_id)
        
        if appointment.doctor_id != doctor.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        treatment = Treatment.query.filter_by(appointment_id=appointment_id).first()
        
        if treatment:
            return make_response(jsonify({
                'diagnosis': treatment.diagnosis,
                'prescription': treatment.prescription,
                'notes': treatment.notes,
                'follow_up_required': treatment.follow_up_required,
                'follow_up_date': treatment.follow_up_date.strftime('%Y-%m-%d') if treatment.follow_up_date else None
            }), 200)
        
        return make_response(jsonify({}), 200)
    
    @auth_token_required
    @roles_required('doctor')
    def post(self, appointment_id):
        doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
        appointment = Appointment.query.get_or_404(appointment_id)
        
        if appointment.doctor_id != doctor.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        data = request.get_json()
        
        treatment = Treatment.query.filter_by(appointment_id=appointment_id).first()
        
        if treatment:
            treatment.diagnosis = data.get('diagnosis', treatment.diagnosis)
            treatment.prescription = data.get('prescription', treatment.prescription)
            treatment.notes = data.get('notes', treatment.notes)
            treatment.follow_up_required = data.get('follow_up_required', treatment.follow_up_required)
            if data.get('follow_up_date'):
                treatment.follow_up_date = datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date()
        else:
            treatment = Treatment(
                appointment_id=appointment_id,
                diagnosis=data['diagnosis'],
                prescription=data.get('prescription'),
                notes=data.get('notes'),
                follow_up_required=data.get('follow_up_required', False),
                follow_up_date=datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date() if data.get('follow_up_date') else None
            )
            db.session.add(treatment)
        
        appointment.status = 'Completed'
        db.session.commit()
        
        return make_response(jsonify({'message': 'Treatment added successfully'}), 201)

class DoctorPatientHistoryAPI(Resource):
    @auth_token_required
    @roles_required('doctor')
    def get(self, patient_id):
        doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
        
        appointments = Appointment.query.filter_by(
            doctor_id=doctor.id,
            patient_id=patient_id,
            status='Completed'
        ).order_by(Appointment.appointment_date.desc()).all()
        
        history = []
        for apt in appointments:
            treatment = Treatment.query.filter_by(appointment_id=apt.id).first()
            history.append({
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'diagnosis': treatment.diagnosis if treatment else None,
                'prescription': treatment.prescription if treatment else None,
                'notes': treatment.notes if treatment else None
            })
        
        return make_response(jsonify(history), 200)

class DoctorProfileAPI(Resource):
    @auth_token_required
    @roles_required('doctor')
    def get(self):
        doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
        
        return make_response(jsonify({
            'username': doctor.user.username,
            'email': doctor.user.email,
            'phone': doctor.user.phone,
            'department': doctor.department.name,
            'department_id': doctor.department_id,
            'qualification': doctor.qualification,
            'experience_years': doctor.experience_years
        }), 200)
    
    @auth_token_required
    @roles_required('doctor')
    def put(self):
        doctor = Doctor.query.filter_by(user_id=current_user.id).first_or_404()
        data = request.get_json()
        
        doctor.user.username = data.get('username', doctor.user.username)
        doctor.user.phone = data.get('phone', doctor.user.phone)
        doctor.qualification = data.get('qualification', doctor.qualification)
        doctor.experience_years = data.get('experience_years', doctor.experience_years)
        
        db.session.commit()
        
        return make_response(jsonify({'message': 'Profile updated successfully'}), 200)