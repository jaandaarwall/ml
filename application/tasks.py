from celery import shared_task
from datetime import datetime, date, timedelta
import csv
import os
from .mail import send_email
from .models import db, Appointment, Patient, Doctor

@shared_task(ignore_results=False, name="application.tasks.send_daily_reminders")
def send_daily_reminders():
    """Send daily appointment reminders to patients"""
    from app import app
    
    with app.app_context():
        today = date.today()
        
        # Get all appointments scheduled for today with status 'Booked'
        appointments = Appointment.query.filter(
            Appointment.appointment_date == today,
            Appointment.status == 'Booked'
        ).all()
        
        reminders_sent = 0
        
        for appointment in appointments:
            patient = Patient.query.get(appointment.patient_id)
            doctor = Doctor.query.get(appointment.doctor_id)
            
            if patient and doctor:
                patient_user = patient.user
                doctor_user = doctor.user
                
                # Create reminder message
                message = f"""
                <html>
                <body>
                    <h2>Appointment Reminder</h2>
                    <p>Dear {patient_user.full_name},</p>
                    <p>This is a reminder for your appointment scheduled today:</p>
                    <ul>
                        <li><strong>Doctor:</strong> Dr. {doctor_user.full_name}</li>
                        <li><strong>Department:</strong> {doctor.department.name}</li>
                        <li><strong>Date:</strong> {appointment.appointment_date.strftime('%d %B %Y')}</li>
                        <li><strong>Time:</strong> {appointment.appointment_time.strftime('%I:%M %p')}</li>
                    </ul>
                    <p>Please arrive 10 minutes before your scheduled time.</p>
                    <p>Best regards,<br>Hospital Management Team</p>
                </body>
                </html>
                """
                
                # Send email
                if send_email(patient_user.email, "Appointment Reminder - Today", message):
                    reminders_sent += 1
                    
        return f"Daily reminders sent: {reminders_sent}"


@shared_task(ignore_results=False, name="application.tasks.send_monthly_reports")
def send_monthly_reports():
    """Send monthly activity reports to doctors"""
    from app import app
    
    with app.app_context():
        # Get first and last day of previous month
        today = date.today()
        first_day_this_month = date(today.year, today.month, 1)
        last_day_prev_month = first_day_this_month - timedelta(days=1)
        first_day_prev_month = date(last_day_prev_month.year, last_day_prev_month.month, 1)
        
        doctors = Doctor.query.filter_by(is_active=True).all()
        reports_sent = 0
        
        for doctor in doctors:
            # Get appointments for this doctor in previous month
            appointments = Appointment.query.filter(
                Appointment.doctor_id == doctor.id,
                Appointment.appointment_date >= first_day_prev_month,
                Appointment.appointment_date <= last_day_prev_month
            ).all()
            
            if not appointments:
                continue
            
            # Calculate statistics
            total_appointments = len(appointments)
            completed = len([a for a in appointments if a.status == 'Completed'])
            cancelled = len([a for a in appointments if a.status == 'Cancelled'])
            
            # Create HTML report
            message = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #4CAF50; color: white; }}
                </style>
            </head>
            <body>
                <h2>Monthly Activity Report - {last_day_prev_month.strftime('%B %Y')}</h2>
                <p>Dear Dr. {doctor.user.full_name},</p>
                
                <h3>Summary</h3>
                <ul>
                    <li><strong>Total Appointments:</strong> {total_appointments}</li>
                    <li><strong>Completed:</strong> {completed}</li>
                    <li><strong>Cancelled:</strong> {cancelled}</li>
                </ul>
                
                <h3>Appointment Details</h3>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Patient</th>
                        <th>Status</th>
                        <th>Diagnosis</th>
                    </tr>
            """
            
            for apt in appointments:
                patient_name = apt.patient.user.full_name
                diagnosis = apt.treatment.diagnosis if apt.treatment else "N/A"
                message += f"""
                    <tr>
                        <td>{apt.appointment_date.strftime('%d-%m-%Y')}</td>
                        <td>{patient_name}</td>
                        <td>{apt.status}</td>
                        <td>{diagnosis[:50]}...</td>
                    </tr>
                """
            
            message += """
                </table>
                <p>Thank you for your dedication!</p>
                <p>Best regards,<br>Hospital Management Team</p>
            </body>
            </html>
            """
            
            subject = f"Monthly Report - {last_day_prev_month.strftime('%B %Y')}"
            if send_email(doctor.user.email, subject, message):
                reports_sent += 1
        
        return f"Monthly reports sent to {reports_sent} doctors"


@shared_task(ignore_results=False, name="application.tasks.export_treatment_csv")
def export_treatment_csv(patient_id):
    """Export patient's treatment history as CSV"""
    from app import app
    
    with app.app_context():
        patient = Patient.query.get(patient_id)
        if not patient:
            return {"success": False, "message": "Patient not found"}
        
        # Get all completed appointments with treatments
        appointments = Appointment.query.filter(
            Appointment.patient_id == patient_id,
            Appointment.status == 'Completed'
        ).order_by(Appointment.appointment_date.desc()).all()
        
        # Create CSV file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"treatment_history_{patient_id}_{timestamp}.csv"
        filepath = os.path.join('static', filename)
        
        # Ensure static directory exists
        os.makedirs('static', exist_ok=True)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Appointment Date', 
                'Doctor Name', 
                'Department', 
                'Diagnosis', 
                'Prescription', 
                'Notes', 
                'Follow-up Required',
                'Follow-up Date'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for apt in appointments:
                doctor = Doctor.query.get(apt.doctor_id)
                treatment = apt.treatment
                
                writer.writerow({
                    'Appointment Date': apt.appointment_date.strftime('%d-%m-%Y'),
                    'Doctor Name': f"Dr. {doctor.user.full_name}",
                    'Department': doctor.department.name,
                    'Diagnosis': treatment.diagnosis if treatment else 'N/A',
                    'Prescription': treatment.prescription if treatment else 'N/A',
                    'Notes': treatment.notes if treatment else 'N/A',
                    'Follow-up Required': 'Yes' if (treatment and treatment.follow_up_required) else 'No',
                    'Follow-up Date': treatment.follow_up_date.strftime('%d-%m-%Y') if (treatment and treatment.follow_up_date) else 'N/A'
                })
        
        # Send notification email to patient
        message = f"""
        <html>
        <body>
            <h2>Treatment History Export</h2>
            <p>Dear {patient.user.full_name},</p>
            <p>Your treatment history has been successfully exported.</p>
            <p>The CSV file is ready for download.</p>
            <p>Best regards,<br>Hospital Management Team</p>
        </body>
        </html>
        """
        
        send_email(patient.user.email, "Treatment History Export Ready", message)
        
        return {
            "success": True, 
            "filename": filename,
            "filepath": filepath,
            "message": "CSV export completed successfully"
        }
