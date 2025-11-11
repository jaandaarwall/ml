from celery import shared_task
from .models import User, Appointment
from .mail import send_email
from datetime import datetime, date, timedelta
import csv

@shared_task
def send_daily_reminders():
    today = date.today()
    appointments = Appointment.query.filter_by(appointment_date=today).all()
    for app in appointments:
        send_email(
            to_address=app.patient.user.email,
            subject='Appointment Reminder',
            message=f'Hi {app.patient.user.full_name}, you have an appointment with Dr. {app.doctor.user.full_name} today at {app.appointment_time}.'
        )

@shared_task
def generate_monthly_report():
    doctors = User.query.filter(User.roles.any(name='doctor')).all()
    for doctor in doctors:
        today = date.today()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = (first_day_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.doctor.id,
            Appointment.appointment_date >= first_day_of_month,
            Appointment.appointment_date <= last_day_of_month
        ).all()

        report = f"<h1>Monthly Report for Dr. {doctor.full_name}</h1>"
        report += "<table><tr><th>Date</th><th>Patient</th><th>Diagnosis</th><th>Prescription</th></tr>"
        for app in appointments:
            if app.treatment:
                report += f"<tr><td>{app.appointment_date}</td><td>{app.patient.user.full_name}</td><td>{app.treatment.diagnosis}</td><td>{app.treatment.prescription}</td></tr>"
        report += "</table>"

        send_email(
            to_address=doctor.email,
            subject='Monthly Report',
            message=report
        )

@shared_task
def export_patient_history(patient_id):
    patient = User.query.get(patient_id)
    appointments = Appointment.query.filter_by(patient_id=patient.patient.id, status='Completed').all()

    csv_file = f'patient_{patient_id}_history.csv'
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Appointment Date', 'Doctor', 'Diagnosis', 'Prescription'])
        for app in appointments:
            if app.treatment:
                writer.writerow([app.appointment_date, app.doctor.user.full_name, app.treatment.diagnosis, app.treatment.prescription])

    # In a real application, you would typically upload this file to a cloud storage
    # and send a download link to the user.
    send_email(
        to_address=patient.email,
        subject='Patient History Export',
        message=f'Your patient history has been exported. Please find the attached file.'
    )
