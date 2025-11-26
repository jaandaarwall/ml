from flask_restful import Resource
from flask import jsonify
from flask_security import auth_token_required, roles_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta

from .Sqldatabase import db
from .models import Appointment, Doctor, Patient, Department, Payment


# ---------------------------------------
# ADMIN ANALYTICS
# ---------------------------------------
class AdminAnalyticsAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        # Monthly Appointments (Last 12 Months)
        monthly_data = db.session.query(
            func.strftime('%Y-%m', Appointment.appointment_date),
            func.count(Appointment.id)
        ).group_by(func.strftime('%Y-%m', Appointment.appointment_date)).all()

        month_labels = [row[0] for row in monthly_data]
        month_values = [row[1] for row in monthly_data]

        # Revenue Per Month (Successful Payments)
        revenue_data = db.session.query(
            func.strftime('%Y-%m', Payment.created_at),
            func.sum(Payment.amount)
        ).filter(Payment.status == 'Success').group_by(func.strftime('%Y-%m', Payment.created_at)).all()

        revenue_labels = [row[0] for row in revenue_data]
        revenue_values = [row[1] for row in revenue_data]

        # Doctors Per Department
        dept_stats = db.session.query(
            Department.name,
            func.count(Doctor.id)
        ).outerjoin(Doctor).group_by(Department.id).all()

        dept_labels = [row[0] for row in dept_stats]
        dept_values = [row[1] for row in dept_stats]

        # Appointment Status Summary
        status_stats = db.session.query(
            Appointment.status,
            func.count(Appointment.id)
        ).group_by(Appointment.status).all()

        status_labels = [row[0] for row in status_stats]
        status_values = [row[1] for row in status_stats]

        return jsonify({
            "appointments_per_month": {
                "labels": month_labels,
                "values": month_values
            },
            "revenue_per_month": {
                "labels": revenue_labels,
                "values": revenue_values
            },
            "doctors_per_department": {
                "labels": dept_labels,
                "values": dept_values
            },
            "appointment_status_summary": {
                "labels": status_labels,
                "values": status_values
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

        # Appointments Per Month
        monthly_data = db.session.query(
            func.strftime('%Y-%m', Appointment.appointment_date),
            func.count(Appointment.id)
        ).filter(
            Appointment.patient_id == patient.id
        ).group_by(func.strftime('%Y-%m', Appointment.appointment_date)).all()

        month_labels = [row[0] for row in monthly_data]
        month_values = [row[1] for row in monthly_data]

        # Money Spent vs Date (Successful Payments Only)
        money_data = db.session.query(
            func.strftime('%Y-%m-%d', Payment.created_at),
            func.sum(Payment.amount)
        ).join(Appointment).filter(
            Appointment.patient_id == patient.id,
            Payment.status.in_(['Success', 'Refunded']) # Include refunded to show activity, or just Success for net spend. Let's show transaction volume.
            # Actually, for "Money Spent", let's stick to 'Success' to show actual expenditure.
        ).filter(
            Payment.status == 'Success'
        ).group_by(func.strftime('%Y-%m-%d', Payment.created_at)).order_by(func.strftime('%Y-%m-%d', Payment.created_at)).all()

        money_labels = [row[0] for row in money_data]
        money_values = [row[1] for row in money_data]

        return jsonify({
            "appointments_per_month": {
                "labels": month_labels,
                "values": month_values
            },
            "money_spent_vs_date": {
                "labels": money_labels,
                "values": money_values
            }
        })