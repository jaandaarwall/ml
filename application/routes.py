from flask import Blueprint, render_template, request, jsonify, send_from_directory
from flask_security import auth_required, roles_required, current_user, hash_password
from flask_security.utils import verify_password
from werkzeug.security import generate_password_hash
from .models import db, User, Roles, Doctor, Patient, Department, Appointment, Treatment, DoctorAvailability
from datetime import datetime, date, time, timedelta
from . import cache
from . import user_datastore
from .celery_init import celery

main = Blueprint('main', __name__)

# ============= PUBLIC ROUTES =============
@main.route('/')
def index():
    """Main landing page"""
    return render_template('index.html', user=current_user)


@main.route('/api/register', methods=['POST'])
def register():
    """Patient registration"""
    try:
        data = request.get_json()

        # Validation
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Username, email, and password are required'}), 400

        # Check if user exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400

        # Create user
        user = user_datastore.create_user(
            username=data['username'],
            full_name=data.get('full_name', data['username']),
            email=data['email'],
            password=hash_password(data['password']),
            phone=data.get('phone'),
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date() if data.get('date_of_birth') else None,
            gender=data.get('gender'),
            address=data.get('address'),
            blood_group=data.get('blood_group'),
            active=True,
            roles=['patient']
        )

        db.session.flush()

        # Create patient profile
        patient = Patient(user_id=user.id)
        db.session.add(patient)
        db.session.commit()

        return jsonify({
            'message': 'Registration successful',
            'user_id': user.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/login', methods=['POST'])
def login():
    """User login (all roles)"""
    try:
        data = request.get_json()

        user = User.query.filter_by(email=data['email']).first()

        if not user or not verify_password(data['password'], user.password):
            return jsonify({'error': 'Invalid credentials'}), 401

        if not user.active:
            return jsonify({'error': 'Account deactivated'}), 403

        # Get user role
        role = user.roles[0].name if user.roles else None

        # Generate token
        token = user.get_auth_token()

        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'email': user.email,
                'role': role
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= ADMIN ROUTES =============
@main.route('/api/admin/dashboard', methods=['GET'])
@auth_required('token')
@roles_required('admin')
@cache.cached(timeout=60, key_prefix='admin_dashboard')
def admin_dashboard():
    """Admin dashboard statistics"""
    try:
        total_doctors = Doctor.query.filter_by(is_active=True).count()
        total_patients = Patient.query.count()
        total_appointments = Appointment.query.count()

        today = date.today()
        today_appointments = Appointment.query.filter_by(appointment_date=today).count()

        # Recent appointments
        recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(10).all()

        appointments_data = []
        for apt in recent_appointments:
            appointments_data.append({
                'id': apt.id,
                'patient_name': apt.patient.user.full_name,
                'doctor_name': apt.doctor.user.full_name,
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'time': apt.appointment_time.strftime('%H:%M'),
                'status': apt.status
            })

        return jsonify({
            'total_doctors': total_doctors,
            'total_patients': total_patients,
            'total_appointments': total_appointments,
            'today_appointments': today_appointments,
            'recent_appointments': appointments_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/admin/doctors', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def admin_get_doctors():
    """Get all doctors"""
    try:
        doctors = Doctor.query.all()

        doctors_data = []
        for doc in doctors:
            doctors_data.append({
                'id': doc.id,
                'user_id': doc.user.id,
                'name': doc.user.full_name,
                'email': doc.user.email,
                'phone': doc.user.phone,
                'department': doc.department.name,
                'qualification': doc.qualification,
                'experience_years': doc.experience_years,
                'is_active': doc.is_active
            })

        return jsonify(doctors_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/admin/doctor', methods=['POST'])
@auth_required('token')
@roles_required('admin')
def admin_add_doctor():
    """Add new doctor"""
    try:
        data = request.get_json()

        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400

        # Create user
        user = user_datastore.create_user(
            username=data['username'],
            full_name=data['full_name'],
            email=data['email'],
            password=hash_password(data['password']),
            phone=data.get('phone'),
            active=True,
            roles=['doctor']
        )

        db.session.flush()

        # Create doctor profile
        doctor = Doctor(
            user_id=user.id,
            department_id=data['department_id'],
            qualification=data.get('qualification'),
            experience_years=data.get('experience_years', 0),
            is_active=True
        )

        db.session.add(doctor)
        db.session.commit()

        cache.delete('admin_dashboard')

        return jsonify({'message': 'Doctor added successfully', 'doctor_id': doctor.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/admin/doctor/<int:doctor_id>', methods=['PUT'])
@auth_required('token')
@roles_required('admin')
def admin_update_doctor(doctor_id):
    """Update doctor details"""
    try:
        doctor = Doctor.query.get_or_404(doctor_id)
        data = request.get_json()

        # Update user info
        user = doctor.user
        user.full_name = data.get('full_name', user.full_name)
        user.email = data.get('email', user.email)
        user.phone = data.get('phone', user.phone)

        # Update doctor info
        doctor.department_id = data.get('department_id', doctor.department_id)
        doctor.qualification = data.get('qualification', doctor.qualification)
        doctor.experience_years = data.get('experience_years', doctor.experience_years)

        db.session.commit()
        cache.delete('admin_dashboard')

        return jsonify({'message': 'Doctor updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/admin/doctor/<int:doctor_id>/toggle', methods=['POST'])
@auth_required('token')
@roles_required('admin')
def admin_toggle_doctor(doctor_id):
    """Activate/Deactivate doctor"""
    try:
        doctor = Doctor.query.get_or_404(doctor_id)
        doctor.is_active = not doctor.is_active
        doctor.user.active = doctor.is_active

        db.session.commit()
        cache.delete('admin_dashboard')

        status = 'activated' if doctor.is_active else 'deactivated'
        return jsonify({'message': f'Doctor {status} successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/admin/patients', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def admin_get_patients():
    """Get all patients"""
    try:
        patients = Patient.query.all()

        patients_data = []
        for pat in patients:
            patients_data.append({
                'id': pat.id,
                'user_id': pat.user.id,
                'name': pat.user.full_name,
                'email': pat.user.email,
                'phone': pat.user.phone,
                'blood_group': pat.user.blood_group,
                'is_active': pat.user.active,
                'created_at': pat.created_at.strftime('%Y-%m-%d')
            })

        return jsonify(patients_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/admin/patient/<int:patient_id>/toggle', methods=['POST'])
@auth_required('token')
@roles_required('admin')
def admin_toggle_patient(patient_id):
    """Activate/Deactivate patient"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        patient.user.active = not patient.user.active

        db.session.commit()

        status = 'activated' if patient.user.active else 'deactivated'
        return jsonify({'message': f'Patient {status} successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/admin/appointments', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def admin_get_appointments():
    """Get all appointments"""
    try:
        appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()

        appointments_data = []
        for apt in appointments:
            appointments_data.append({
                'id': apt.id,
                'patient_name': apt.patient.user.full_name,
                'patient_id': apt.patient_id,
                'doctor_name': apt.doctor.user.full_name,
                'doctor_id': apt.doctor_id,
                'department': apt.doctor.department.name,
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'time': apt.appointment_time.strftime('%H:%M'),
                'status': apt.status,
                'reason': apt.reason
            })

        return jsonify(appointments_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/admin/search', methods=['GET'])
@auth_required('token')
@roles_required('admin')
def admin_search():
    """Search doctors and patients"""
    try:
        query = request.args.get('q', '').lower()
        search_type = request.args.get('type', 'all')  # all, doctor, patient

        results = {'doctors': [], 'patients': []}

        if search_type in ['all', 'doctor']:
            doctors = Doctor.query.join(User).filter(
                (User.full_name.ilike(f'%{query}%')) |
                (User.email.ilike(f'%{query}%'))
            ).all()

            for doc in doctors:
                results['doctors'].append({
                    'id': doc.id,
                    'name': doc.user.full_name,
                    'email': doc.user.email,
                    'department': doc.department.name,
                    'is_active': doc.is_active
                })

        if search_type in ['all', 'patient']:
            patients = Patient.query.join(User).filter(
                (User.full_name.ilike(f'%{query}%')) |
                (User.email.ilike(f'%{query}%')) |
                (User.phone.ilike(f'%{query}%'))
            ).all()

            for pat in patients:
                results['patients'].append({
                    'id': pat.id,
                    'name': pat.user.full_name,
                    'email': pat.user.email,
                    'phone': pat.user.phone,
                    'is_active': pat.user.active
                })

        return jsonify(results), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= DOCTOR ROUTES =============
@main.route('/api/doctor/dashboard', methods=['GET'])
@auth_required('token')
@roles_required('doctor')
def doctor_dashboard():
    """Doctor dashboard"""
    try:
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()

        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        today = date.today()
        week_end = today + timedelta(days=7)

        # Today's appointments
        today_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == today,
            Appointment.status == 'Booked'
        ).count()

        # Upcoming appointments (next 7 days)
        upcoming = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date.between(today, week_end),
            Appointment.status == 'Booked'
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()

        # Total patients seen
        total_patients = db.session.query(Appointment.patient_id).filter(
            Appointment.doctor_id == doctor.id,
            Appointment.status == 'Completed'
        ).distinct().count()

        upcoming_data = []
        for apt in upcoming:
            upcoming_data.append({
                'id': apt.id,
                'patient_name': apt.patient.user.full_name,
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'time': apt.appointment_time.strftime('%H:%M'),
                'reason': apt.reason,
                'status': apt.status
            })

        return jsonify({
            'today_appointments': today_appointments,
            'upcoming_appointments': upcoming_data,
            'total_patients': total_patients
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/doctor/appointments', methods=['GET'])
@auth_required('token')
@roles_required('doctor')
def doctor_get_appointments():
    """Get doctor's appointments"""
    try:
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()

        appointments = Appointment.query.filter_by(doctor_id=doctor.id).order_by(
            Appointment.appointment_date.desc()
        ).all()

        appointments_data = []
        for apt in appointments:
            appointments_data.append({
                'id': apt.id,
                'patient_name': apt.patient.user.full_name,
                'patient_id': apt.patient_id,
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'time': apt.appointment_time.strftime('%H:%M'),
                'reason': apt.reason,
                'status': apt.status,
                'has_treatment': apt.treatment is not None
            })

        return jsonify(appointments_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/doctor/appointment/<int:appointment_id>/complete', methods=['POST'])
@auth_required('token')
@roles_required('doctor')
def doctor_complete_appointment(appointment_id):
    """Mark appointment as completed"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)

        # Verify doctor owns this appointment
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if appointment.doctor_id != doctor.id:
            return jsonify({'error': 'Unauthorized'}), 403

        appointment.status = 'Completed'
        db.session.commit()

        return jsonify({'message': 'Appointment marked as completed'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/doctor/appointment/<int:appointment_id>/treatment', methods=['POST', 'PUT'])
@auth_required('token')
@roles_required('doctor')
def doctor_add_treatment(appointment_id):
    """Add/Update treatment details"""
    try:
        appointment = Appointment.query.get_or_404(appointment_id)
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()

        if appointment.doctor_id != doctor.id:
            return jsonify({'error': 'Unauthorized'}), 403

        data = request.get_json()

        treatment = appointment.treatment
        if not treatment:
            treatment = Treatment(appointment_id=appointment_id)
            db.session.add(treatment)

        treatment.diagnosis = data.get('diagnosis', treatment.diagnosis)
        treatment.prescription = data.get('prescription', treatment.prescription)
        treatment.notes = data.get('notes', treatment.notes)
        treatment.follow_up_required = data.get('follow_up_required', False)

        if data.get('follow_up_date'):
            treatment.follow_up_date = datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date()

        # Auto-complete appointment
        appointment.status = 'Completed'

        db.session.commit()

        return jsonify({'message': 'Treatment added successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/doctor/availability', methods=['GET', 'POST'])
@auth_required('token')
@roles_required('doctor')
def doctor_availability():
    """Get or add doctor availability"""
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()

    if request.method == 'GET':
        try:
            today = date.today()
            week_end = today + timedelta(days=7)

            availability = DoctorAvailability.query.filter(
                DoctorAvailability.doctor_id == doctor.id,
                DoctorAvailability.date.between(today, week_end)
            ).order_by(DoctorAvailability.date).all()

            availability_data = []
            for av in availability:
                availability_data.append({
                    'id': av.id,
                    'date': av.date.strftime('%Y-%m-%d'),
                    'start_time': av.start_time.strftime('%H:%M'),
                    'end_time': av.end_time.strftime('%H:%M'),
                    'max_patients': av.max_patients,
                    'is_available': av.is_available
                })

            return jsonify(availability_data), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        try:
            data = request.get_json()

            availability_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(data['start_time'], '%H:%M').time()
            end_time = datetime.strptime(data['end_time'], '%H:%M').time()

            # Check if already exists
            existing = DoctorAvailability.query.filter_by(
                doctor_id=doctor.id,
                date=availability_date
            ).first()

            if existing:
                return jsonify({'error': 'Availability already set for this date'}), 400

            availability = DoctorAvailability(
                doctor_id=doctor.id,
                date=availability_date,
                start_time=start_time,
                end_time=end_time,
                max_patients=data.get('max_patients', 10),
                is_available=True
            )

            db.session.add(availability)
            db.session.commit()

            return jsonify({'message': 'Availability added successfully'}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500


@main.route('/api/doctor/availability/<int:availability_id>', methods=['DELETE'])
@auth_required('token')
@roles_required('doctor')
def doctor_delete_availability(availability_id):
    """Delete availability slot"""
    try:
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        availability = DoctorAvailability.query.get_or_404(availability_id)

        if availability.doctor_id != doctor.id:
            return jsonify({'error': 'Unauthorized'}), 403

        db.session.delete(availability)
        db.session.commit()

        return jsonify({'message': 'Availability deleted'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/doctor/patients', methods=['GET'])
@auth_required('token')
@roles_required('doctor')
def doctor_get_patients():
    """Get doctor's patients"""
    try:
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()

        # Get unique patients
        patient_ids = db.session.query(Appointment.patient_id).filter(
            Appointment.doctor_id == doctor.id
        ).distinct().all()

        patients_data = []
        for (patient_id,) in patient_ids:
            patient = Patient.query.get(patient_id)
            if patient:
                # Count appointments
                appointment_count = Appointment.query.filter_by(
                    doctor_id=doctor.id,
                    patient_id=patient_id
                ).count()

                patients_data.append({
                    'id': patient.id,
                    'name': patient.user.full_name,
                    'email': patient.user.email,
                    'phone': patient.user.phone,
                    'blood_group': patient.user.blood_group,
                    'appointment_count': appointment_count
                })

        return jsonify(patients_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/doctor/patient/<int:patient_id>/history', methods=['GET'])
@auth_required('token')
@roles_required('doctor')
def doctor_patient_history(patient_id):
    """Get patient's medical history with this doctor"""
    try:
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()

        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.patient_id == patient_id,
            Appointment.status == 'Completed'
        ).order_by(Appointment.appointment_date.desc()).all()

        history_data = []
        for apt in appointments:
            treatment = apt.treatment
            history_data.append({
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'diagnosis': treatment.diagnosis if treatment else 'N/A',
                'prescription': treatment.prescription if treatment else 'N/A',
                'notes': treatment.notes if treatment else 'N/A',
                'follow_up_required': treatment.follow_up_required if treatment else False,
                'follow_up_date': treatment.follow_up_date.strftime('%Y-%m-%d') if (treatment and treatment.follow_up_date) else None
            })

        return jsonify(history_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= PATIENT ROUTES =============
@main.route('/api/patient/dashboard', methods=['GET'])
@auth_required('token')
@roles_required('patient')
def patient_dashboard():
    """Patient dashboard"""
    try:
        patient = Patient.query.filter_by(user_id=current_user.id).first()

        if not patient:
            return jsonify({'error': 'Patient profile not found'}), 404

        # Upcoming appointments
        today = date.today()
        upcoming = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.appointment_date >= today,
            Appointment.status == 'Booked'
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).limit(5).all()

        # Past appointments
        past = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.status.in_(['Completed', 'Cancelled'])
        ).order_by(Appointment.appointment_date.desc()).limit(5).all()

        # Departments
        departments = Department.query.all()

        upcoming_data = []
        for apt in upcoming:
            upcoming_data.append({
                'id': apt.id,
                'doctor_name': apt.doctor.user.full_name,
                'department': apt.doctor.department.name,
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'time': apt.appointment_time.strftime('%H:%M'),
                'status': apt.status
            })

        past_data = []
        for apt in past:
            past_data.append({
                'id': apt.id,
                'doctor_name': apt.doctor.user.full_name,
                'department': apt.doctor.department.name,
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'time': apt.appointment_time.strftime('%H:%M'),
                'status': apt.status
            })

        departments_data = [{'id': d.id, 'name': d.name, 'description': d.description} for d in departments]

        return jsonify({
            'profile': {
                'name': current_user.full_name,
                'email': current_user.email,
                'phone': current_user.phone,
                'blood_group': current_user.blood_group
            },
            'upcoming_appointments': upcoming_data,
            'past_appointments': past_data,
            'departments': departments_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/patient/doctors', methods=['GET'])
@auth_required('token')
@roles_required('patient')
@cache.cached(timeout=120, query_string=True)
def patient_get_doctors():
    """Get doctors (optionally filter by department)"""
    try:
        department_id = request.args.get('department_id', type=int)

        query = Doctor.query.filter_by(is_active=True)

        if department_id:
            query = query.filter_by(department_id=department_id)

        doctors = query.all()

        doctors_data = []
        for doc in doctors:
            doctors_data.append({
                'id': doc.id,
                'name': doc.user.full_name,
                'email': doc.user.email,
                'department': doc.department.name,
                'qualification': doc.qualification,
                'experience_years': doc.experience_years
            })

        return jsonify(doctors_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/patient/doctor/<int:doctor_id>/availability', methods=['GET'])
@auth_required('token')
@roles_required('patient')
def patient_doctor_availability(doctor_id):
    """Get doctor's available time slots"""
    try:
        selected_date = request.args.get('date')
        if not selected_date:
            return jsonify({'error': 'Date parameter required'}), 400

        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()

        # Get doctor's availability for the date
        availability = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            date=selected_date,
            is_available=True
        ).first()

        if not availability:
            return jsonify({'slots': []}), 200

        # Generate 30-minute time slots
        slots = []
        current_time = datetime.combine(selected_date, availability.start_time)
        end_time = datetime.combine(selected_date, availability.end_time)

        while current_time < end_time:
            slot_time = current_time.time()

            # Check how many appointments already booked for this slot
            booked_count = Appointment.query.filter(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == selected_date,
                Appointment.appointment_time == slot_time,
                Appointment.status == 'Booked'
            ).count()

            if booked_count < availability.max_patients:
                slots.append({
                    'time': slot_time.strftime('%H:%M'),
                    'available': True
                })

            current_time += timedelta(minutes=30)

        return jsonify({'slots': slots}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/patient/appointment/book', methods=['POST'])
@auth_required('token')
@roles_required('patient')
def patient_book_appointment():
    """Book an appointment"""
    try:
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        data = request.get_json()

        doctor_id = data['doctor_id']
        appointment_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        appointment_time = datetime.strptime(data['time'], '%H:%M').time()

        # Check if doctor has availability
        availability = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            date=appointment_date,
            is_available=True
        ).first()

        if not availability:
            return jsonify({'error': 'Doctor not available on this date'}), 400

        # Check if slot is full
        booked_count = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.status == 'Booked'
        ).count()

        if booked_count >= availability.max_patients:
            return jsonify({'error': 'This time slot is fully booked'}), 400

        # Create appointment
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=data.get('reason', ''),
            status='Booked'
        )

        db.session.add(appointment)
        db.session.commit()

        cache.delete('admin_dashboard')

        return jsonify({
            'message': 'Appointment booked successfully',
            'appointment_id': appointment.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/patient/appointments', methods=['GET'])
@auth_required('token')
@roles_required('patient')
def patient_get_appointments():
    """Get patient's appointments"""
    try:
        patient = Patient.query.filter_by(user_id=current_user.id).first()

        appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(
            Appointment.appointment_date.desc()
        ).all()

        appointments_data = []
        for apt in appointments:
            appointments_data.append({
                'id': apt.id,
                'doctor_name': apt.doctor.user.full_name,
                'department': apt.doctor.department.name,
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'time': apt.appointment_time.strftime('%H:%M'),
                'reason': apt.reason,
                'status': apt.status,
                'has_treatment': apt.treatment is not None
            })

        return jsonify(appointments_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/patient/appointment/<int:appointment_id>/cancel', methods=['POST'])
@auth_required('token')
@roles_required('patient')
def patient_cancel_appointment(appointment_id):
    """Cancel an appointment"""
    try:
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        appointment = Appointment.query.get_or_404(appointment_id)

        if appointment.patient_id != patient.id:
            return jsonify({'error': 'Unauthorized'}), 403

        if appointment.status != 'Booked':
            return jsonify({'error': 'Can only cancel booked appointments'}), 400

        appointment.status = 'Cancelled'
        db.session.commit()

        cache.delete('admin_dashboard')

        return jsonify({'message': 'Appointment cancelled successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main.route('/api/patient/history', methods=['GET'])
@auth_required('token')
@roles_required('patient')
def patient_medical_history():
    """Get patient's medical history"""
    try:
        patient = Patient.query.filter_by(user_id=current_user.id).first()

        appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.status == 'Completed'
        ).order_by(Appointment.appointment_date.desc()).all()

        history_data = []
        for apt in appointments:
            treatment = apt.treatment
            history_data.append({
                'id': apt.id,
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'doctor_name': apt.doctor.user.full_name,
                'department': apt.doctor.department.name,
                'diagnosis': treatment.diagnosis if treatment else 'N/A',
                'prescription': treatment.prescription if treatment else 'N/A',
                'notes': treatment.notes if treatment else 'N/A',
                'follow_up_required': treatment.follow_up_required if treatment else False,
                'follow_up_date': treatment.follow_up_date.strftime('%Y-%m-%d') if (treatment and treatment.follow_up_date) else None
            })

        return jsonify(history_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/patient/profile', methods=['GET', 'PUT'])
@auth_required('token')
@roles_required('patient')
def patient_profile():
    """Get or update patient profile"""
    if request.method == 'GET':
        try:
            return jsonify({
                'username': current_user.username,
                'full_name': current_user.full_name,
                'email': current_user.email,
                'phone': current_user.phone,
                'date_of_birth': current_user.date_of_birth.strftime('%Y-%m-%d') if current_user.date_of_birth else None,
                'gender': current_user.gender,
                'address': current_user.address,
                'blood_group': current_user.blood_group
            }), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'PUT':
        try:
            data = request.get_json()

            current_user.full_name = data.get('full_name', current_user.full_name)
            current_user.phone = data.get('phone', current_user.phone)
            current_user.address = data.get('address', current_user.address)
            current_user.gender = data.get('gender', current_user.gender)
            current_user.blood_group = data.get('blood_group', current_user.blood_group)

            if data.get('date_of_birth'):
                current_user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()

            db.session.commit()

            return jsonify({'message': 'Profile updated successfully'}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500


@main.route('/api/patient/export-history', methods=['POST'])
@auth_required('token')
@roles_required('patient')
def patient_export_history():
    """Trigger CSV export of treatment history"""
    try:
        from .tasks import export_treatment_csv
        patient = Patient.query.filter_by(user_id=current_user.id).first()

        # Trigger Celery task
        task = export_treatment_csv.delay(patient.id)

        return jsonify({
            'message': 'Export started. You will receive an email when ready.',
            'task_id': task.id
        }), 202

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/patient/export-status/<task_id>', methods=['GET'])
@auth_required('token')
@roles_required('patient')
def patient_export_status(task_id):
    """Check status of CSV export task"""
    try:
        task = celery.AsyncResult(task_id)

        if task.state == 'PENDING':
            response = {'state': task.state, 'status': 'Task is pending...'}
        elif task.state == 'SUCCESS':
            response = {
                'state': task.state,
                'result': task.result
            }
        else:
            response = {'state': task.state, 'status': str(task.info)}

        return jsonify(response), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/static/<path:filename>')
def download_file(filename):
    """Serve static files (CSV downloads)"""
    return send_from_directory('static', filename)


# ============= COMMON ROUTES =============
@main.route('/api/departments', methods=['GET'])
@cache.cached(timeout=3600)
def get_departments():
    """Get all departments"""
    try:
        departments = Department.query.all()

        departments_data = []
        for dept in departments:
            # Count active doctors in department
            doctor_count = Doctor.query.filter_by(
                department_id=dept.id,
                is_active=True
            ).count()

            departments_data.append({
                'id': dept.id,
                'name': dept.name,
                'description': dept.description,
                'doctor_count': doctor_count
            })

        return jsonify(departments_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/user/profile', methods=['GET'])
@auth_required('token')
def get_user_profile():
    """Get current user profile"""
    try:
        role = current_user.roles[0].name if current_user.roles else None

        profile = {
            'id': current_user.id,
            'username': current_user.username,
            'full_name': current_user.full_name,
            'email': current_user.email,
            'phone': current_user.phone,
            'role': role
        }

        if role == 'doctor':
            doctor = Doctor.query.filter_by(user_id=current_user.id).first()
            if doctor:
                profile['doctor_id'] = doctor.id
                profile['department'] = doctor.department.name
                profile['qualification'] = doctor.qualification

        elif role == 'patient':
            patient = Patient.query.filter_by(user_id=current_user.id).first()
            if patient:
                profile['patient_id'] = patient.id
                profile['blood_group'] = current_user.blood_group

        return jsonify(profile), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
