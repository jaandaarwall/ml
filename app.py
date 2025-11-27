from flask import Flask, render_template, jsonify
from backend.celery_app import celery_init_app
from backend.tasks import example_task, send_daily_reminders, sheduler_task, send_monthly_reports, check_missed_appointments
from celery.schedules import crontab
from backend.config import Config
from backend.Sqldatabase import db
from backend.models import *
from backend.user_datastore import user_datastore
from flask_security import Security, utils
import time
from backend.payment_apis import DummyPaymentAPI
# Import the cache instance
from backend.cache import cache


from flask_restful import Api
from flask_cors import CORS

from backend.task_apis import (
    TaskExampleAPI,
    TaskSendEmailAPI,
    TaskMonthlyReportAPI,
    TaskPatientCSVAPI,
    TaskAdminAppointmentsCSVAPI,
    TaskAdminTransactionsCSVAPI,
    TaskDoctorAppointmentsCSVAPI,
    TaskStatusAPI
)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    # Initialize Cache
    cache.init_app(app)
    
    security = Security(app, user_datastore)

    api = Api(app, prefix='/api')
    return app, api 
       
app, api = create_app()
CORS(app, origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ])
celery = celery_init_app(app)
celery.autodiscover_tasks()


def init_db(app):
    with app.app_context():
        db.create_all()

        admin_role = user_datastore.find_or_create_role(name='admin', description='Administrator')
        doctor_role = user_datastore.find_or_create_role(name='doctor', description='Doctor')
        user_role = user_datastore.find_or_create_role(name='user', description='User')

        # Ensure departments exist first
        cardiology = None
        for dept_data in [
            {'name': 'Cardiology', 'description': 'Heart and cardiovascular system', 'price': 300.0},
            {'name': 'Neurology', 'description': 'Brain and nervous system', 'price': 400.0},
            {'name': 'Orthopedics', 'description': 'Bones and muscles', 'price': 500.0},
            {'name': 'Pediatrics', 'description': 'Children healthcare', 'price': 600.0},
            {'name': 'Dermatology', 'description': 'Skin, hair, and nails', 'price': 700.0},
            {'name': 'General Medicine', 'description': 'General health issues', 'price': 800.0}
        ]:
            existing = Department.query.filter_by(name=dept_data['name']).first()
            if not existing:
                dept = Department(**dept_data)
                db.session.add(dept)
                if dept_data['name'] == 'Cardiology':
                    cardiology = dept
            elif dept_data['name'] == 'Cardiology':
                cardiology = existing
        
        db.session.commit()

        # Create or Update Admin User
        admin = user_datastore.find_user(email='admin@hospital.com')
        if not admin:
            admin = user_datastore.create_user(
                username='admin',
                email='admin@hospital.com',
                password=utils.hash_password('admin123'),
                active=True,
                roles=[admin_role, doctor_role, user_role]
            )
            db.session.commit()

        # Ensure Admin has a Doctor Profile (since they have the doctor role)
        if doctor_role in admin.roles:
            admin_doctor = Doctor.query.filter_by(user_id=admin.id).first()
            if not admin_doctor:
                # Fetch Cardiology department for default admin doctor profile
                if not cardiology:
                    cardiology = Department.query.filter_by(name='Cardiology').first()
                
                admin_doctor = Doctor(
                    user_id=admin.id,
                    department_id=cardiology.id if cardiology else 1,
                    qualification="MBBS, MD (Admin)",
                    experience_years=10,
                    is_active=True
                )
                db.session.add(admin_doctor)
                db.session.commit()

        # Ensure Admin has a Patient Profile (since they have the user role)
        if user_role in admin.roles:
            admin_patient = Patient.query.filter_by(user_id=admin.id).first()
            if not admin_patient:
                admin_patient = Patient(user_id=admin.id)
                db.session.add(admin_patient)
                db.session.commit()


from backend.authentication_apis import LoginAPI, LogoutAPI, RegisterAPI, CheckEmailAPI
from backend.admin_apis import (AdminDashboardAPI, AdminDoctorsAPI, AdminAddDoctorAPI, 
                                AdminDoctorDetailAPI, AdminPatientsAPI, AdminPatientDetailAPI,
                                AdminAppointmentsAPI, AdminSearchAPI, DepartmentsAPI,AdminTransactionsAPI)
from backend.doctor_apis import (DoctorDashboardAPI, DoctorAppointmentsAPI, DoctorPatientsAPI,
                                 DoctorAvailabilityAPI, DoctorCompleteAppointmentAPI, DoctorTreatmentAPI,
                                 DoctorPatientHistoryAPI, DoctorProfileAPI, DoctorAvailabilitySlotAPI)
from backend.patient_apis import (PatientDashboardAPI, PatientDoctorsAPI, PatientDoctorAvailabilityAPI,
                                  PatientBookAppointmentAPI, PatientAppointmentsAPI, PatientCancelAppointmentAPI,
                                  PatientHistoryAPI, PatientProfileAPI, PatientAvailableDatesAPI, PatientRescheduleAppointmentAPI)

# Auth APIs
api.add_resource(LoginAPI, '/login')
api.add_resource(LogoutAPI, '/logout')
api.add_resource(RegisterAPI, '/register')
api.add_resource(CheckEmailAPI, '/check-email')

# Admin APIs
api.add_resource(AdminDashboardAPI, '/admin/dashboard')
api.add_resource(AdminDoctorsAPI, '/admin/doctors')
api.add_resource(AdminAddDoctorAPI, '/admin/doctor/add')
api.add_resource(AdminDoctorDetailAPI, '/admin/doctor/<int:doctor_id>')
api.add_resource(AdminPatientsAPI, '/admin/patients')
api.add_resource(AdminPatientDetailAPI, '/admin/patient/<int:patient_id>')
api.add_resource(AdminAppointmentsAPI, '/admin/appointments')
api.add_resource(AdminSearchAPI, '/admin/search')
api.add_resource(AdminTransactionsAPI, '/admin/transactions')

# Doctor APIs
api.add_resource(DoctorDashboardAPI, '/doctor/dashboard')
api.add_resource(DoctorAppointmentsAPI, '/doctor/appointments')
api.add_resource(DoctorPatientsAPI, '/doctor/patients')
api.add_resource(DoctorAvailabilityAPI, '/doctor/availability')
api.add_resource(DoctorAvailabilitySlotAPI, '/doctor/availability/<int:availability_id>/slot')
api.add_resource(DoctorCompleteAppointmentAPI, '/doctor/appointment/<int:appointment_id>/complete')
api.add_resource(DoctorTreatmentAPI, '/doctor/appointment/<int:appointment_id>/treatment')
api.add_resource(DoctorPatientHistoryAPI, '/doctor/patient/<int:patient_id>/history')
api.add_resource(DoctorProfileAPI, '/doctor/profile')

# Patient APIs
api.add_resource(PatientDashboardAPI, '/patient/dashboard')
api.add_resource(PatientDoctorsAPI, '/patient/doctors')
api.add_resource(PatientDoctorAvailabilityAPI, '/patient/doctor/<int:doctor_id>/availability')
api.add_resource(PatientBookAppointmentAPI, '/patient/book/<int:doctor_id>')
api.add_resource(PatientAppointmentsAPI, '/patient/appointments')
api.add_resource(PatientCancelAppointmentAPI, '/patient/appointment/<int:appointment_id>/cancel')
api.add_resource(PatientRescheduleAppointmentAPI, '/patient/appointment/<int:appointment_id>/reschedule')
api.add_resource(PatientHistoryAPI, '/patient/history')
api.add_resource(PatientProfileAPI, '/patient/profile')
api.add_resource(PatientAvailableDatesAPI, '/patient/doctor/<int:doctor_id>/available-dates')

# General APIs
api.add_resource(DepartmentsAPI, '/departments')
api.add_resource(DummyPaymentAPI, '/payment/<int:payment_id>/pay')



@celery.on_after_finalize.connect 
def setup_periodic_tasks(sender, **kwargs):
    # Send daily reminders at 8 AM every day
    sender.add_periodic_task(
        crontab(),
        # crontab(minute=0, hour=8),
        send_daily_reminders.s(),
        name='Daily appointment reminders'
    )
    
    # Check for missed appointments daily at 9 PM
    sender.add_periodic_task(
        crontab(minute=0, hour=21),
        check_missed_appointments.s(),
        name='Mark missed appointments'
    )
    
    # Send monthly reports on the 1st of every month at 6 AM
    sender.add_periodic_task(
        crontab(),
        # crontab(minute=0, hour=6, day_of_month=1),
        send_monthly_reports.s(),
        name='Monthly doctor activity reports'
    )


# Task APIs
api.add_resource(TaskExampleAPI, '/task/example')
api.add_resource(TaskSendEmailAPI, '/task/send-email')
api.add_resource(TaskMonthlyReportAPI, '/task/monthly-report')
api.add_resource(TaskPatientCSVAPI, '/task/export-patient-csv')
api.add_resource(TaskAdminAppointmentsCSVAPI, '/task/export-admin-appointments')
api.add_resource(TaskAdminTransactionsCSVAPI, '/task/export-admin-transactions')
api.add_resource(TaskDoctorAppointmentsCSVAPI, '/task/export-doctor-appointments')
api.add_resource(TaskStatusAPI, '/task/status/<string:task_id>')

from backend.analytics_api import (
    AdminAnalyticsAPI,
    DoctorAnalyticsAPI,
    PatientAnalyticsAPI
)

# Analytics APIs
api.add_resource(AdminAnalyticsAPI, '/admin/analytics')
api.add_resource(DoctorAnalyticsAPI, '/doctor/analytics')
api.add_resource(PatientAnalyticsAPI, '/patient/analytics')


if __name__ == "__main__":
    init_db(app) 
    app.run(debug=True)