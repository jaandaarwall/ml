import time
from celery import shared_task
from .mail import send_email
from datetime import datetime, timedelta
import csv
import io


@shared_task(ignore_results=False, name = "This is a example task")
def example_task():
    time.sleep(10)
    print("example task")
    return {
        "message":"task completed"
        }, 200

@shared_task(ignore_results=False, name = "this is the example of sending email")
def sheduler_task(to_email, subject, body):
    send_email(to_email, subject, body)
    print("sheduler task")
    return {
        "message":"sheduler task completed"
        }, 200

@shared_task(ignore_results=False, name = "Daily appointment reminders")
def send_daily_reminders():
    from .models import Appointment
    from .Sqldatabase import db
    from flask import current_app
    
    today = datetime.now().date()
    
    appointments = Appointment.query.filter_by(
        appointment_date=today,
        status='Booked'
    ).all()
    
    for apt in appointments:
        patient_email = apt.patient.user.email
        doctor_name = apt.doctor.user.username
        time = apt.appointment_time.strftime('%H:%M')
        
        subject = "Appointment Reminder"
        body = f"Hello {apt.patient.user.username},\n\nThis is a reminder that you have an appointment today with Dr. {doctor_name} at {time}.\n\nPlease arrive 10 minutes early.\n\nThank you!"
        
        send_email(patient_email, subject, body)
    
    return {"message": f"Sent {len(appointments)} reminders", "count": len(appointments)}


@shared_task(ignore_results=False, name = "Monthly doctor activity report")
def send_monthly_reports():
    from .models import Doctor, Appointment, Treatment
    from .Sqldatabase import db
    from datetime import datetime
    
    last_month = datetime.now().replace(day=1) - timedelta(days=1)
    start_date = last_month.replace(day=1)
    end_date = last_month
    
    doctors = Doctor.query.filter_by(is_active=True).all()
    
    for doctor in doctors:
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date.between(start_date, end_date)
        ).all()
        
        completed = [apt for apt in appointments if apt.status == 'Completed']
        
        html_body = f"""
        <html>
        <head><title>Monthly Activity Report</title></head>
        <body>
            <h2>Monthly Activity Report - {last_month.strftime('%B %Y')}</h2>
            <h3>Dr. {doctor.user.username}</h3>
            <p><strong>Total Appointments:</strong> {len(appointments)}</p>
            <p><strong>Completed:</strong> {len(completed)}</p>
            <p><strong>Cancelled:</strong> {len([a for a in appointments if a.status == 'Cancelled'])}</p>
            
            <h3>Completed Appointments Details:</h3>
            <table border="1" cellpadding="5">
                <tr>
                    <th>Date</th>
                    <th>Patient</th>
                    <th>Diagnosis</th>
                </tr>
        """
        
        for apt in completed:
            treatment = Treatment.query.filter_by(appointment_id=apt.id).first()
            diagnosis = treatment.diagnosis if treatment else 'N/A'
            html_body += f"""
                <tr>
                    <td>{apt.appointment_date.strftime('%Y-%m-%d')}</td>
                    <td>{apt.patient.user.username}</td>
                    <td>{diagnosis}</td>
                </tr>
            """
        
        html_body += """
            </table>
        </body>
        </html>
        """
        
        send_email(doctor.user.email, f"Monthly Report - {last_month.strftime('%B %Y')}", html_body)
    
    return {"message": f"Sent reports to {len(doctors)} doctors"}


@shared_task(ignore_results=False, name = "Export patient treatment history as CSV")
def export_patient_csv(patient_id):
    from .models import Patient, Appointment, Treatment
    
    patient = Patient.query.get(patient_id)
    if not patient:
        return {"error": "Patient not found"}
    
    appointments = Appointment.query.filter_by(
        patient_id=patient_id,
        status='Completed'
    ).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Patient ID', 'Patient Name', 'Doctor Name', 'Appointment Date', 
                     'Diagnosis', 'Prescription', 'Treatment Notes', 'Follow-up Required', 'Follow-up Date'])
    
    for apt in appointments:
        treatment = Treatment.query.filter_by(appointment_id=apt.id).first()
        
        writer.writerow([
            patient.id,
            patient.user.username,
            apt.doctor.user.username,
            apt.appointment_date.strftime('%Y-%m-%d'),
            treatment.diagnosis if treatment else '',
            treatment.prescription if treatment else '',
            treatment.notes if treatment else '',
            'Yes' if treatment and treatment.follow_up_required else 'No',
            treatment.follow_up_date.strftime('%Y-%m-%d') if treatment and treatment.follow_up_date else ''
        ])
    
    csv_data = output.getvalue()
    
    # Send email with CSV
    send_email(
        patient.user.email,
        "Your Treatment History Export",
        f"Hello {patient.user.username},\n\nYour treatment history export is attached.\n\nCSV Data:\n{csv_data}"
    )
    
    return {"message": "CSV export completed", "patient_id": patient_id}


