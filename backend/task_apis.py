from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_security import auth_token_required, roles_required, current_user
from celery.result import AsyncResult
from .tasks import (
    example_task,
    sheduler_task,
    send_daily_reminders,
    send_monthly_reports,
    export_patient_csv,
    export_admin_appointments_csv,
    export_admin_transactions_csv,
    export_doctor_appointments_csv
)
from .models import Doctor


# -------------------------------
# Trigger normal example task
# -------------------------------
class TaskExampleAPI(Resource):
    @auth_token_required
    def get(self):
        task = example_task.delay()
        return make_response(jsonify({
            "message": "Task started",
            "task_id": task.id
        }), 202)


# -------------------------------
# Trigger manual email sending
# -------------------------------
class TaskSendEmailAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def post(self):
        data = request.get_json()

        to_email = data.get("to_email")
        subject = data.get("subject")
        body = data.get("body")

        if not to_email or not subject or not body:
            return make_response(jsonify({"message": "Missing required fields"}), 400)

        task = sheduler_task.delay(to_email, subject, body)

        return make_response(jsonify({
            "message": "Email task queued",
            "task_id": task.id
        }), 202)


# -------------------------------
# Trigger monthly reports manually
# -------------------------------
class TaskMonthlyReportAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        task = send_monthly_reports.delay()
        return make_response(jsonify({
            "message": "Monthly report task queued",
            "task_id": task.id
        }), 202)


# -------------------------------
# Export patient history as CSV
# -------------------------------
class TaskPatientCSVAPI(Resource):
    @auth_token_required
    @roles_required('user')
    def post(self):
        data = request.get_json() or {}
        from .models import Patient
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not patient:
             return make_response(jsonify({"message": "Patient profile not found"}), 404)

        start_date = data.get('start_date')
        end_date = data.get('end_date')

        task = export_patient_csv.delay(patient.id, start_date, end_date)

        return make_response(jsonify({
            "message": "Export generating...",
            "task_id": task.id
        }), 202)

# -------------------------------
# Admin Exports
# -------------------------------
class TaskAdminAppointmentsCSVAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def post(self):
        data = request.get_json() or {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        task = export_admin_appointments_csv.delay(current_user.email, start_date, end_date)
        
        return make_response(jsonify({
            "message": "Export generating...",
            "task_id": task.id
        }), 202)

class TaskAdminTransactionsCSVAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def post(self):
        data = request.get_json() or {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        task = export_admin_transactions_csv.delay(current_user.email, start_date, end_date)
        
        return make_response(jsonify({
            "message": "Export generating...",
            "task_id": task.id
        }), 202)

# -------------------------------
# Doctor Export
# -------------------------------
class TaskDoctorAppointmentsCSVAPI(Resource):
    @auth_token_required
    @roles_required('doctor')
    def post(self):
        data = request.get_json() or {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if not doctor:
            return make_response(jsonify({"message": "Doctor profile not found"}), 404)
            
        task = export_doctor_appointments_csv.delay(doctor.id, current_user.email, start_date, end_date)
        
        return make_response(jsonify({
            "message": "Export generating...",
            "task_id": task.id
        }), 202)

# -------------------------------
# General Task Status
# -------------------------------
class TaskStatusAPI(Resource):
    @auth_token_required
    def get(self, task_id):
        task_result = AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            response = {
                'state': 'PENDING',
                'status': 'Task is pending...'
            }
        elif task_result.state != 'FAILURE':
            response = {
                'state': 'SUCCESS',
                'result': task_result.result
            }
        else:
            response = {
                'state': 'FAILURE',
                'status': str(task_result.info),
            }
        return make_response(jsonify(response), 200)