from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_security import auth_token_required, roles_required
from .tasks import (
    example_task,
    sheduler_task,
    send_daily_reminders,
    send_monthly_reports,
    export_patient_csv
)


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
# Trigger daily appointment reminders manually
# -------------------------------
class TaskDailyReminderAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self):
        task = send_daily_reminders.delay()
        return make_response(jsonify({
            "message": "Daily reminder task queued",
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
# Export patient history as CSV via task
# -------------------------------
class TaskPatientCSVAPI(Resource):
    @auth_token_required
    @roles_required('user')
    def post(self):
        data = request.get_json()
        patient_id = data.get("patient_id")

        if not patient_id:
            return make_response(jsonify({"message": "patient_id required"}), 400)

        task = export_patient_csv.delay(patient_id)

        return make_response(jsonify({
            "message": "CSV export task started",
            "task_id": task.id
        }), 202)
