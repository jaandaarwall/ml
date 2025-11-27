import time
from celery import shared_task
from .mail import send_email
from datetime import datetime, timedelta
import csv
import io
from .models import *
from .Sqldatabase import db

@shared_task(ignore_results=False, name="This is a example task")
def example_task():
    time.sleep(10)
    print("example task")
    return {"message": "task completed"}, 200

@shared_task(ignore_results=False, name="this is the example of sending email")
def sheduler_task(to_email, subject, body):
    send_email(to_email, subject, body)
    print("sheduler task")
    return {"message": "sheduler task completed"}, 200

@shared_task(ignore_results=False, name="Daily appointment reminders")
def send_daily_reminders():
    today = datetime.now().date()
    
    appointments = Appointment.query.filter_by(
        appointment_date=today,
        status='Booked'
    ).all()
    
    for apt in appointments:
        patient_email = apt.patient.user.email
        doctor_name = apt.doctor.user.username
        time_str = apt.appointment_time.strftime('%H:%M')
        
        subject = "Appointment Reminder"
        body = f"Hello {apt.patient.user.username},\n\nThis is a reminder that you have an appointment today with Dr. {doctor_name} at {time_str}.\n\nPlease arrive 10 minutes early.\n\nThank you!"
        
        send_email(patient_email, subject, body)
    
    return {"message": f"Sent {len(appointments)} reminders", "count": len(appointments)}

@shared_task(ignore_results=False, name="Check Missed Appointments (9 PM)")
def check_missed_appointments():
    today = datetime.now().date()
    
    # Find appointments scheduled for today that are still 'Booked' (not Completed/Cancelled)
    missed_appointments = Appointment.query.filter_by(
        appointment_date=today,
        status='Booked'
    ).all()
    
    count = 0
    for apt in missed_appointments:
        # Update status to Action Pending (was Missed)
        apt.status = 'Action Pending'
        db.session.add(apt)
        
        # Send Email
        patient_email = apt.patient.user.email
        doctor_name = apt.doctor.user.username
        
        subject = "Appointment Missed - Action Required"
        body = f"""Hello {apt.patient.user.username},

It seems you missed your appointment today with Dr. {doctor_name}.

Your appointment status has been updated to 'Action Pending'.
Please login to the portal and go to 'My Appointments' to reschedule this appointment.

Best regards,
Hospital Management Team"""
        
        send_email(patient_email, subject, body)
        count += 1
    
    db.session.commit()
    return {"message": f"Marked {count} appointments as Action Pending", "count": count}

@shared_task(ignore_results=False, name="Monthly doctor activity report")
def send_monthly_reports():
    # Calculate previous month range
    today = datetime.now()
    first_day_this_month = today.replace(day=1)
    last_day_prev_month = first_day_this_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)
    
    start_date = first_day_prev_month.date()
    end_date = last_day_prev_month.date()
    
    doctors = Doctor.query.filter_by(is_active=True).all()
    
    for doctor in doctors:
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date.between(start_date, end_date)
        ).all()
        
        completed = [apt for apt in appointments if apt.status == 'Completed']
        cancelled = [apt for apt in appointments if apt.status == 'Cancelled']
        
        html_body = f"""
        <html>
        <head><title>Monthly Activity Report</title></head>
        <body>
            <h2>Monthly Activity Report - {last_day_prev_month.strftime('%B %Y')}</h2>
            <h3>Dr. {doctor.user.username}</h3>
            <p><strong>Total Appointments:</strong> {len(appointments)}</p>
            <p><strong>Completed:</strong> {len(completed)}</p>
            <p><strong>Cancelled:</strong> {len(cancelled)}</p>
            
            <h3>Completed Appointments Details:</h3>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #f2f2f2;">
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
        
        send_email(doctor.user.email, f"Monthly Report - {last_day_prev_month.strftime('%B %Y')}", html_body)
    
    return {"message": f"Sent reports to {len(doctors)} doctors"}

@shared_task(ignore_results=False, name="Export patient treatment history as CSV")
def export_patient_csv(patient_id, start_date=None, end_date=None):
    patient = Patient.query.get(patient_id)
    if not patient:
        return {"error": "Patient not found"}
    
    query = Appointment.query.filter_by(
        patient_id=patient_id,
        status='Completed'
    )

    if start_date and end_date:
        s_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        e_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(Appointment.appointment_date.between(s_date, e_date))

    appointments = query.all()
    
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
    
    return {
        "csv_data": csv_data,
        "filename": f"medical_history_{patient.user.username}_{datetime.now().strftime('%Y%m%d')}.csv"
    }

@shared_task(ignore_results=False, name="Export all appointments as CSV (Admin)")
def export_admin_appointments_csv(admin_email, start_date=None, end_date=None):
    query = Appointment.query

    if start_date and end_date:
        s_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        e_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(Appointment.appointment_date.between(s_date, e_date))
    
    appointments = query.order_by(Appointment.appointment_date.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Patient', 'Doctor', 'Date', 'Time', 'Status', 'Reason'])
    
    for apt in appointments:
        writer.writerow([
            apt.id,
            apt.patient.user.username,
            apt.doctor.user.username,
            apt.appointment_date.strftime('%Y-%m-%d'),
            apt.appointment_time.strftime('%H:%M'),
            apt.status,
            apt.reason or ''
        ])
        
    csv_data = output.getvalue()
    
    return {
        "csv_data": csv_data,
        "filename": f"all_appointments_{datetime.now().strftime('%Y%m%d')}.csv"
    }

@shared_task(ignore_results=False, name="Export transactions as CSV (Admin)")
def export_admin_transactions_csv(admin_email, start_date=None, end_date=None):
    query = Payment.query

    if start_date and end_date:
        s_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        e_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        query = query.filter(Payment.created_at.between(s_date, e_date))
    
    payments = query.order_by(Payment.created_at.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Transaction ID', 'Appointment ID', 'Patient', 'Doctor', 'Amount', 'Status', 'Date'])
    
    for pay in payments:
        patient_name = pay.appointment.patient.user.username if pay.appointment and pay.appointment.patient else 'Unknown'
        doctor_name = pay.appointment.doctor.user.username if pay.appointment and pay.appointment.doctor else 'Unknown'
        
        writer.writerow([
            pay.id,
            pay.appointment_id,
            patient_name,
            doctor_name,
            pay.amount,
            pay.status,
            pay.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
        
    csv_data = output.getvalue()
    
    return {
        "csv_data": csv_data,
        "filename": f"transactions_{datetime.now().strftime('%Y%m%d')}.csv"
    }

@shared_task(ignore_results=False, name="Export doctor appointments as CSV")
def export_doctor_appointments_csv(doctor_id, doctor_email, start_date=None, end_date=None):
    query = Appointment.query.filter_by(doctor_id=doctor_id)

    if start_date and end_date:
        s_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        e_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(Appointment.appointment_date.between(s_date, e_date))
    
    appointments = query.order_by(Appointment.appointment_date.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Date', 'Time', 'Patient Name', 'Status', 'Reason'])
    
    for apt in appointments:
        writer.writerow([
            apt.id,
            apt.appointment_date.strftime('%Y-%m-%d'),
            apt.appointment_time.strftime('%H:%M'),
            apt.patient.user.username,
            apt.status,
            apt.reason or ''
        ])
        
    csv_data = output.getvalue()
    
    return {
        "csv_data": csv_data,
        "filename": f"my_appointments_{datetime.now().strftime('%Y%m%d')}.csv"
    }