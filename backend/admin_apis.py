from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_security import auth_token_required, roles_required, current_user
from .Sqldatabase import db
from .models import *
from .user_datastore import user_datastore
from datetime import datetime

class AdminDashboardAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        total_doctors = Doctor.query.filter_by(is_active=True).count()
        total_patients = Patient.query.count()
        total_appointments = Appointment.query.count()
        today_appointments = Appointment.query.filter_by(appointment_date=datetime.now().date()).count()
        
        return make_response(jsonify({
            'total_doctors': total_doctors,
            'total_patients': total_patients,
            'total_appointments': total_appointments,
            'today_appointments': today_appointments
        }), 200)

class AdminDoctorsAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        doctors = Doctor.query.all()
        doctors_list = []
        for doc in doctors:
            doctors_list.append({
                'id': doc.id,
                'name': doc.user.username,
                'email': doc.user.email,
                'phone': doc.user.phone,
                'department': doc.department.name,
                'qualification': doc.qualification,
                'experience_years': doc.experience_years,
                'is_active': doc.is_active
            })
        return make_response(jsonify(doctors_list), 200)

class AdminAddDoctorAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def post(self):
        data = request.get_json()
        
        if user_datastore.find_user(email=data['email']):
            return make_response(jsonify({'message': 'Email already exists'}), 409)
        
        doctor_role = user_datastore.find_role('doctor')
        user_role = user_datastore.find_role('user')
        
        user = user_datastore.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            phone=data.get('phone'),
            roles=[doctor_role, user_role]
        )
        
        doctor = Doctor(
            user_id=user.id,
            department_id=data['department_id'],
            qualification=data.get('qualification'),
            experience_years=data.get('experience_years', 0)
        )
        db.session.add(doctor)
        db.session.commit()
        
        return make_response(jsonify({'message': 'Doctor added successfully'}), 201)

class AdminDoctorDetailAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self, doctor_id):
        doctor = Doctor.query.get_or_404(doctor_id)
        appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
        
        return make_response(jsonify({
            'doctor': {
                'id': doctor.id,
                'name': doctor.user.username,
                'email': doctor.user.email,
                'phone': doctor.user.phone,
                'department': doctor.department.name,
                'qualification': doctor.qualification,
                'experience_years': doctor.experience_years,
                'is_active': doctor.is_active
            },
            'appointments_count': len(appointments)
        }), 200)
    
    @auth_token_required
    @roles_required('admin')
    def put(self, doctor_id):
        data = request.get_json()
        doctor = Doctor.query.get_or_404(doctor_id)
        
        doctor.user.username = data.get('username', doctor.user.username)
        doctor.user.phone = data.get('phone', doctor.user.phone)
        doctor.department_id = data.get('department_id', doctor.department_id)
        doctor.qualification = data.get('qualification', doctor.qualification)
        doctor.experience_years = data.get('experience_years', doctor.experience_years)
        
        db.session.commit()
        return make_response(jsonify({'message': 'Doctor updated successfully'}), 200)
    
    @auth_token_required
    @roles_required('admin')
    def delete(self, doctor_id):
        doctor = Doctor.query.get_or_404(doctor_id)
        doctor.is_active = not doctor.is_active
        doctor.user.active = doctor.is_active
        db.session.commit()
        
        status = 'activated' if doctor.is_active else 'deactivated'
        return make_response(jsonify({'message': f'Doctor {status} successfully'}), 200)

class AdminPatientsAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        patients = Patient.query.all()
        patients_list = []
        for patient in patients:
            patients_list.append({
                'id': patient.id,
                'name': patient.user.username,
                'email': patient.user.email,
                'phone': patient.user.phone,
                'blood_group': patient.user.blood_group,
                'is_active': patient.user.active
            })
        return make_response(jsonify(patients_list), 200)

class AdminPatientDetailAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self, patient_id):
        patient = Patient.query.get_or_404(patient_id)
        appointments = Appointment.query.filter_by(patient_id=patient_id).all()
        
        appointments_list = []
        for apt in appointments:
            appointments_list.append({
                'id': apt.id,
                'doctor_name': apt.doctor.user.username,
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'time': apt.appointment_time.strftime('%H:%M'),
                'status': apt.status
            })
        
        return make_response(jsonify({
            'patient': {
                'id': patient.id,
                'name': patient.user.username,
                'email': patient.user.email,
                'phone': patient.user.phone,
                'blood_group': patient.user.blood_group,
                'gender': patient.user.gender,
                'dob': patient.user.date_of_birth.strftime('%Y-%m-%d') if patient.user.date_of_birth else None
            },
            'appointments': appointments_list
        }), 200)
    
    @auth_token_required
    @roles_required('admin')
    def delete(self, patient_id):
        patient = Patient.query.get_or_404(patient_id)
        patient.user.active = not patient.user.active
        db.session.commit()
        
        status = 'activated' if patient.user.active else 'deactivated'
        return make_response(jsonify({'message': f'Patient {status} successfully'}), 200)

class AdminAppointmentsAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
        appointments_list = []
        for apt in appointments:
            appointments_list.append({
                'id': apt.id,
                'patient_name': apt.patient.user.username,
                'doctor_name': apt.doctor.user.username,
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'time': apt.appointment_time.strftime('%H:%M'),
                'status': apt.status,
                'reason': apt.reason
            })
        return make_response(jsonify(appointments_list), 200)

class AdminSearchAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        query = request.args.get('q', '')
        search_type = request.args.get('type', 'all')
        
        results = {'doctors': [], 'patients': []}
        
        if search_type in ['all', 'doctor']:
            doctors = Doctor.query.join(User).filter(
                (User.username.ilike(f'%{query}%')) | 
                (User.email.ilike(f'%{query}%'))
            ).all()
            
            for doc in doctors:
                results['doctors'].append({
                    'id': doc.id,
                    'name': doc.user.username,
                    'email': doc.user.email,
                    'department': doc.department.name
                })
        
        if search_type in ['all', 'patient']:
            patients = Patient.query.join(User).filter(
                (User.username.ilike(f'%{query}%')) | 
                (User.email.ilike(f'%{query}%')) |
                (User.phone.ilike(f'%{query}%'))
            ).all()
            
            for patient in patients:
                results['patients'].append({
                    'id': patient.id,
                    'name': patient.user.username,
                    'email': patient.user.email,
                    'phone': patient.user.phone
                })
        
        return make_response(jsonify(results), 200)

class DepartmentsAPI(Resource):
    def get(self):
        departments = Department.query.all()
        dept_list = []
        for dept in departments:
            dept_list.append({
                'id': dept.id,
                'name': dept.name,
                'description': dept.description
            })
        return make_response(jsonify(dept_list), 200)