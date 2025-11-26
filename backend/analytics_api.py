from flask_restful import Resource
from flask import jsonify
from flask_security import auth_token_required, roles_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta

from .Sqldatabase import db
from .models import Appointment, Doctor, Patient, Department, Payment, User


# ---------------------------------------
# ADMIN ANALYTICS
# ---------------------------------------
class AdminAnalyticsAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        # 1. Appointments vs Cancellations per Month
        monthly_appts = db.session.query(
            func.strftime('%Y-%m', Appointment.appointment_date),
            func.count(Appointment.id)
        ).group_by(func.strftime('%Y-%m', Appointment.appointment_date)).all()

        monthly_cancellations = db.session.query(
            func.strftime('%Y-%m', Appointment.appointment_date),
            func.count(Appointment.id)
        ).filter(Appointment.status == 'Cancelled').group_by(func.strftime('%Y-%m', Appointment.appointment_date)).all()

        # Merge Appointment Data
        appt_data_map = {}
        for row in monthly_appts:
            appt_data_map[row[0]] = {'total': row[1], 'cancelled': 0}
        
        for row in monthly_cancellations:
            if row[0] in appt_data_map:
                appt_data_map[row[0]]['cancelled'] = row[1]
            else:
                appt_data_map[row[0]] = {'total': row[1], 'cancelled': row[1]}

        sorted_appt_months = sorted(appt_data_map.keys())
        
        # 2. Revenue vs Refunded (Cancellation Revenue) per Month
        revenue_data = db.session.query(
            func.strftime('%Y-%m', Payment.created_at),
            func.sum(Payment.amount)
        ).filter(Payment.status == 'Success').group_by(func.strftime('%Y-%m', Payment.created_at)).all()

        refund_data = db.session.query(
            func.strftime('%Y-%m', Payment.created_at),
            func.sum(Payment.amount)
        ).filter(Payment.status == 'Refunded').group_by(func.strftime('%Y-%m', Payment.created_at)).all()

        rev_data_map = {}
        for row in revenue_data:
            rev_data_map[row[0]] = {'revenue': row[1], 'refunded': 0}
            
        for row in refund_data:
            refund_val = row[1] * 0.9 if row[1] else 0
            if row[0] in rev_data_map:
                rev_data_map[row[0]]['refunded'] = refund_val
            else:
                rev_data_map[row[0]] = {'revenue': 0, 'refunded': refund_val}

        sorted_rev_months = sorted(rev_data_map.keys())

        # 3. Doctors Per Department
        dept_stats = db.session.query(
            Department.name,
            func.count(Doctor.id)
        ).outerjoin(Doctor).group_by(Department.id).all()

        dept_labels = [row[0] for row in dept_stats]
        dept_values = [row[1] for row in dept_stats]

        # 4. Appointment Status Summary
        status_stats = db.session.query(
            Appointment.status,
            func.count(Appointment.id)
        ).group_by(Appointment.status).all()

        status_labels = [row[0] for row in status_stats]
        status_values = [row[1] for row in status_stats]

        # 5. Top 10 Active Doctors (Current Month)
        today = datetime.now()
        start_of_month = today.replace(day=1)
        # Calculate end of month roughly or just filter >= start_of_month
        # To be precise for "current month", we filter appointment_date between start and end of this month.
        # Or just >= start_of_month if we only care about this month so far.
        
        # Finding last day of month
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
        end_of_month = next_month - timedelta(days=1)

        top_doctors = db.session.query(
            User.username,
            func.count(Appointment.id).label('count')
        ).join(Doctor, Doctor.user_id == User.id)\
         .join(Appointment, Appointment.doctor_id == Doctor.id)\
         .filter(Appointment.appointment_date >= start_of_month.date())\
         .filter(Appointment.appointment_date <= end_of_month.date())\
         .filter(Appointment.status != 'Cancelled')\
         .group_by(User.username)\
         .order_by(func.count(Appointment.id).desc())\
         .limit(10).all()

        top_doc_labels = [row[0] for row in top_doctors]
        top_doc_values = [row[1] for row in top_doctors]

        return jsonify({
            "appointments_per_month": {
                "labels": sorted_appt_months,
                "total": [appt_data_map[m]['total'] for m in sorted_appt_months],
                "cancelled": [appt_data_map[m]['cancelled'] for m in sorted_appt_months]
            },
            "revenue_per_month": {
                "labels": sorted_rev_months,
                "revenue": [rev_data_map[m]['revenue'] for m in sorted_rev_months],
                "refunded": [rev_data_map[m]['refunded'] for m in sorted_rev_months]
            },
            "doctors_per_department": {
                "labels": dept_labels,
                "values": dept_values
            },
            "appointment_status_summary": {
                "labels": status_labels,
                "values": status_values
            },
            "top_active_doctors": {
                "labels": top_doc_labels,
                "values": top_doc_values
            }
        })


# ---------------------------------------
# DOCTOR ANALYTICS
# ---------------------------------------
class DoctorAnalyticsAPI(Resource):
    @auth_token_required
    @roles_required('doctor')
    def get(self):
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()

        if not doctor:
            return jsonify({"error": "Doctor not found"}), 404

        today = datetime.now().date()
        last_7 = today - timedelta(days=6)

        # Last 7 Days Appointments
        week_data = db.session.query(
            func.strftime('%Y-%m-%d', Appointment.appointment_date),
            func.count(Appointment.id)
        ).filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date.between(last_7, today)
        ).group_by(func.strftime('%Y-%m-%d', Appointment.appointment_date)).all()

        week_labels = [row[0] for row in week_data]
        week_values = [row[1] for row in week_data]

        # Appointment Status Breakdown
        status_data = db.session.query(
            Appointment.status,
            func.count(Appointment.id)
        ).filter(Appointment.doctor_id == doctor.id).group_by(Appointment.status).all()

        status_labels = [row[0] for row in status_data]
        status_values = [row[1] for row in status_data]

        return jsonify({
            "last_7_days": {
                "labels": week_labels,
                "values": week_values
            },
            "appointment_status": {
                "labels": status_labels,
                "values": status_values
            }
        })


# ---------------------------------------
# PATIENT ANALYTICS
# ---------------------------------------
class PatientAnalyticsAPI(Resource):
    @auth_token_required
    @roles_required('user')
    def get(self):
        patient = Patient.query.filter_by(user_id=current_user.id).first()

        if not patient:
            return jsonify({"appointments_per_month": {}, "money_spent": {}})

        # Appointments Per Month (Total)
        monthly_data = db.session.query(
            func.strftime('%Y-%m', Appointment.appointment_date),
            func.count(Appointment.id)
        ).filter(
            Appointment.patient_id == patient.id
        ).group_by(func.strftime('%Y-%m', Appointment.appointment_date)).all()

        # Cancellations Per Month
        cancellation_data = db.session.query(
            func.strftime('%Y-%m', Appointment.appointment_date),
            func.count(Appointment.id)
        ).filter(
            Appointment.patient_id == patient.id,
            Appointment.status == 'Cancelled'
        ).group_by(func.strftime('%Y-%m', Appointment.appointment_date)).all()

        # Process and Merge Data
        data_map = {}
        
        # Initialize with total counts
        for row in monthly_data:
            data_map[row[0]] = {'total': row[1], 'cancelled': 0}
            
        # Add cancellation counts
        for row in cancellation_data:
            if row[0] in data_map:
                data_map[row[0]]['cancelled'] = row[1]
            else:
                data_map[row[0]] = {'total': row[1], 'cancelled': row[1]}

        sorted_months = sorted(data_map.keys())
        month_labels = sorted_months
        month_total_values = [data_map[m]['total'] for m in sorted_months]
        month_cancelled_values = [data_map[m]['cancelled'] for m in sorted_months]

        # Money Spent vs Date (Successful Payments Only)
        money_data = db.session.query(
            func.strftime('%Y-%m-%d', Payment.created_at),
            func.sum(Payment.amount)
        ).join(Appointment).filter(
            Appointment.patient_id == patient.id,
            Payment.status == 'Success'
        ).group_by(func.strftime('%Y-%m-%d', Payment.created_at)).order_by(func.strftime('%Y-%m-%d', Payment.created_at)).all()

        money_labels = [row[0] for row in money_data]
        money_values = [row[1] for row in money_data]

        return jsonify({
            "appointments_per_month": {
                "labels": month_labels,
                "total": month_total_values,
                "cancelled": month_cancelled_values
            },
            "money_spent_vs_date": {
                "labels": money_labels,
                "values": money_values
            }
        })