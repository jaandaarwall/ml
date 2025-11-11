from flask import request, jsonify
from flask_restful import Resource, reqparse
from flask_security import auth_required, roles_required, current_user, roles_accepted
from werkzeug.security import check_password_hash
from .models import db, User, Roles, Patient, Doctor, Department, DoctorAvailability, Appointment, Treatment
from .resources import api
from .cache import cache
import uuid
from datetime import datetime

# User registration
class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('full_name', type=str, required=True)
        args = parser.parse_args()

        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already registered'}, 400

        user = api.app.security.datastore.create_user(
            email=args['email'],
            password=args['password'],
            full_name=args['full_name'],
            roles=['patient'],
            fs_uniquifier=str(uuid.uuid4())
        )
        db.session.commit()

        patient = Patient(user_id=user.id)
        db.session.add(patient)
        db.session.commit()

        return {'message': 'Patient registered successfully'}, 201

# User login
class Login(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        user = User.query.filter_by(email=args['email']).first()

        if user and check_password_hash(user.password, args['password']):
            token = user.get_auth_token()
            return {'token': token, 'role': user.roles[0].name}

        return {'message': 'Invalid credentials'}, 401

# User logout
class Logout(Resource):
    @auth_required('token')
    def post(self):
        from flask_security.utils import logout_user
        logout_user()
        return {'message': 'Logged out successfully'}

api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')

# Admin Doctor Management
class AdminDoctor(Resource):
    @auth_required('token')
    @roles_required('admin')
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('full_name', type=str, required=True)
        parser.add_argument('department_id', type=int, required=True)
        parser.add_argument('qualification', type=str, required=True)
        parser.add_argument('experience_years', type=int, required=True)
        args = parser.parse_args()

        if User.query.filter_by(email=args['email']).first():
            return {'message': 'Email already registered'}, 400

        user = api.app.security.datastore.create_user(
            email=args['email'],
            password=args['password'],
            full_name=args['full_name'],
            roles=['doctor'],
            fs_uniquifier=str(uuid.uuid4())
        )
        db.session.commit()

        doctor = Doctor(
            user_id=user.id,
            department_id=args['department_id'],
            qualification=args['qualification'],
            experience_years=args['experience_years']
        )
        db.session.add(doctor)
        db.session.commit()

        return {'message': 'Doctor added successfully'}, 201

    @auth_required('token')
    @roles_required('admin')
    @cache.cached(timeout=300)
    def get(self, doctor_id=None):
        if doctor_id:
            doctor = Doctor.query.get(doctor_id)
            if not doctor:
                return {'message': 'Doctor not found'}, 404
            return {
                'id': doctor.id,
                'full_name': doctor.user.full_name,
                'email': doctor.user.email,
                'department': doctor.department.name,
                'qualification': doctor.qualification,
                'experience_years': doctor.experience_years,
                'is_active': doctor.is_active
            }

        doctors = Doctor.query.all()
        return [{
            'id': doctor.id,
            'full_name': doctor.user.full_name,
            'email': doctor.user.email,
            'department': doctor.department.name
        } for doctor in doctors]

    @auth_required('token')
    @roles_required('admin')
    def put(self, doctor_id):
        parser = reqparse.RequestParser()
        parser.add_argument('full_name', type=str)
        parser.add_argument('department_id', type=int)
        parser.add_argument('qualification', type=str)
        parser.add_argument('experience_years', type=int)
        args = parser.parse_args()

        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return {'message': 'Doctor not found'}, 404

        if args['full_name']:
            doctor.user.full_name = args['full_name']
        if args['department_id']:
            doctor.department_id = args['department_id']
        if args['qualification']:
            doctor.qualification = args['qualification']
        if args['experience_years']:
            doctor.experience_years = args['experience_years']
        db.session.commit()

        return {'message': 'Doctor updated successfully'}

    @auth_required('token')
    @roles_required('admin')
    def delete(self, doctor_id):
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return {'message': 'Doctor not found'}, 404

        doctor.is_active = not doctor.is_active
        doctor.user.active = doctor.is_active
        db.session.commit()

        return {'message': f'Doctor status set to {"active" if doctor.is_active else "inactive"}'}

api.add_resource(AdminDoctor, '/admin/doctor', '/admin/doctor/<int:doctor_id>')

# Admin Patient Management
class AdminPatient(Resource):
    @auth_required('token')
    @roles_required('admin')
    @cache.cached(timeout=300)
    def get(self, patient_id=None):
        if patient_id:
            patient = Patient.query.get(patient_id)
            if not patient:
                return {'message': 'Patient not found'}, 404
            return {
                'id': patient.id,
                'full_name': patient.user.full_name,
                'email': patient.user.email,
                'phone': patient.user.phone,
                'blood_group': patient.user.blood_group,
                'gender': patient.user.gender,
                'address': patient.user.address,
                'date_of_birth': str(patient.user.date_of_birth)
            }

        patients = Patient.query.all()
        return [{
            'id': patient.id,
            'full_name': patient.user.full_name,
            'email': patient.user.email
        } for patient in patients]

    @auth_required('token')
    @roles_required('admin')
    def delete(self, patient_id):
        patient = Patient.query.get(patient_id)
        if not patient:
            return {'message': 'Patient not found'}, 404

        patient.user.active = not patient.user.active
        db.session.commit()

        return {'message': f'Patient status set to {"active" if patient.user.active else "inactive"}'}

api.add_resource(AdminPatient, '/admin/patient', '/admin/patient/<int:patient_id>')

# Search
class Search(Resource):
    @auth_required('token')
    @roles_accepted('admin', 'patient')
    @cache.cached(timeout=300)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('q', type=str, required=True)
        args = parser.parse_args()

        query = args['q']

        doctors = Doctor.query.join(User).join(Department).filter(
            User.full_name.ilike(f'%{query}%') |
            Department.name.ilike(f'%{query}%')
        ).all()

        patients = Patient.query.join(User).filter(
            User.full_name.ilike(f'%{query}%') |
            User.email.ilike(f'%{query}%')
        ).all()

        return {
            'doctors': [{
                'id': doctor.id,
                'full_name': doctor.user.full_name,
                'department': doctor.department.name
            } for doctor in doctors],
            'patients': [{
                'id': patient.id,
                'full_name': patient.user.full_name,
                'email': patient.user.email
            } for patient in patients]
        }

api.add_resource(Search, '/search')

# Doctor Availability
class DoctorAvailabilityResource(Resource):
    @auth_required('token')
    @roles_required('doctor')
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('date', type=str, required=True)
        parser.add_argument('start_time', type=str, required=True)
        parser.add_argument('end_time', type=str, required=True)
        parser.add_argument('total_seats', type=int, required=True)
        args = parser.parse_args()

        doctor = Doctor.query.filter_by(user_id=current_user.id).first()

        availability = DoctorAvailability(
            doctor_id=doctor.id,
            date=datetime.strptime(args['date'], '%Y-%m-%d').date(),
            start_time=datetime.strptime(args['start_time'], '%H:%M:%S').time(),
            end_time=datetime.strptime(args['end_time'], '%H:%M:%S').time(),
            total_seats=args['total_seats']
        )
        db.session.add(availability)
        db.session.commit()

        return {'message': 'Availability added successfully'}, 201

    @auth_required('token')
    @roles_required('doctor')
    def get(self):
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        availabilities = DoctorAvailability.query.filter_by(doctor_id=doctor.id).all()
        return [{
            'id': avail.id,
            'date': str(avail.date),
            'start_time': str(avail.start_time),
            'end_time': str(avail.end_time),
            'total_seats': avail.total_seats,
            'is_available': avail.is_available
        } for avail in availabilities]

api.add_resource(DoctorAvailabilityResource, '/doctor/availability')

# Doctor Appointments
class DoctorAppointmentResource(Resource):
    @auth_required('token')
    @roles_required('doctor')
    def get(self):
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        appointments = Appointment.query.filter_by(doctor_id=doctor.id).all()
        return [{
            'id': app.id,
            'patient_name': app.patient.user.full_name,
            'appointment_date': str(app.appointment_date),
            'appointment_time': str(app.appointment_time),
            'status': app.status
        } for app in appointments]

    @auth_required('token')
    @roles_required('doctor')
    def put(self, appointment_id):
        parser = reqparse.RequestParser()
        parser.add_argument('status', type=str, required=True)
        args = parser.parse_args()

        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return {'message': 'Appointment not found'}, 404

        appointment.status = args['status']
        db.session.commit()

        return {'message': 'Appointment status updated successfully'}

api.add_resource(DoctorAppointmentResource, '/doctor/appointment', '/doctor/appointment/<int:appointment_id>')

# Treatment
class TreatmentResource(Resource):
    @auth_required('token')
    @roles_required('doctor')
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('appointment_id', type=int, required=True)
        parser.add_argument('diagnosis', type=str, required=True)
        parser.add_argument('prescription', type=str, required=True)
        parser.add_argument('notes', type=str)
        args = parser.parse_args()

        treatment = Treatment(
            appointment_id=args['appointment_id'],
            diagnosis=args['diagnosis'],
            prescription=args['prescription'],
            notes=args['notes']
        )
        db.session.add(treatment)

        appointment = Appointment.query.get(args['appointment_id'])
        appointment.status = 'Completed'

        db.session.commit()

        return {'message': 'Treatment added successfully'}, 201

api.add_resource(TreatmentResource, '/doctor/treatment')

# Patient Appointment Booking
class PatientAppointmentResource(Resource):
    @auth_required('token')
    @roles_required('patient')
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('doctor_id', type=int, required=True)
        parser.add_argument('appointment_date', type=str, required=True)
        parser.add_argument('appointment_time', type=str, required=True)
        parser.add_argument('reason', type=str)
        args = parser.parse_args()

        patient = Patient.query.filter_by(user_id=current_user.id).first()

        # Check for conflicts
        existing_appointment = Appointment.query.filter_by(
            doctor_id=args['doctor_id'],
            appointment_date=args['appointment_date'],
            appointment_time=args['appointment_time']
        ).first()

        if existing_appointment:
            return {'message': 'Appointment slot not available'}, 400

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=args['doctor_id'],
            appointment_date=datetime.strptime(args['appointment_date'], '%Y-%m-%d').date(),
            appointment_time=datetime.strptime(args['appointment_time'], '%H:%M:%S').time(),
            reason=args['reason']
        )
        db.session.add(appointment)
        db.session.commit()

        return {'message': 'Appointment booked successfully'}, 201

    @auth_required('token')
    @roles_required('patient')
    def get(self):
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        appointments = Appointment.query.filter_by(patient_id=patient.id).all()
        return [{
            'id': app.id,
            'doctor_name': app.doctor.user.full_name,
            'appointment_date': str(app.appointment_date),
            'appointment_time': str(app.appointment_time),
            'status': app.status
        } for app in appointments]

    @auth_required('token')
    @roles_required('patient')
    def put(self, appointment_id):
        parser = reqparse.RequestParser()
        parser.add_argument('status', type=str, required=True)
        args = parser.parse_args()

        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return {'message': 'Appointment not found'}, 404

        appointment.status = args['status']
        db.session.commit()

        return {'message': 'Appointment status updated successfully'}

api.add_resource(PatientAppointmentResource, '/patient/appointment', '/patient/appointment/<int:appointment_id>')

# Treatment History
class TreatmentHistoryResource(Resource):
    @auth_required('token')
    @roles_accepted('patient', 'doctor')
    def get(self, patient_id=None):
        if current_user.has_role('patient'):
            patient = Patient.query.filter_by(user_id=current_user.id).first()
            appointments = Appointment.query.filter_by(patient_id=patient.id, status='Completed').all()
        elif current_user.has_role('doctor'):
            if not patient_id:
                return {'message': 'Patient ID is required'}, 400
            appointments = Appointment.query.filter_by(patient_id=patient_id, doctor_id=current_user.doctor.id, status='Completed').all()
        else:
            return {'message': 'Unauthorized'}, 401

        return [{
            'appointment_date': str(app.appointment_date),
            'doctor_name': app.doctor.user.full_name,
            'diagnosis': app.treatment.diagnosis,
            'prescription': app.treatment.prescription,
            'notes': app.treatment.notes
        } for app in appointments]

api.add_resource(TreatmentHistoryResource, '/history', '/history/<int:patient_id>')
