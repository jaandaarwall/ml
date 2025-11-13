
#####


# app.py
from flask import Flask, render_template, jsonify
from backend.celery_app import celery_init_app
from backend.tasks import example_task, sheduler_task
from celery.schedules import crontab
from backend.config import Config
from backend.Sqldatabase import db
from backend.models import *
from backend.user_datastore import user_datastore
from flask_security import Security
import time
from werkzeug.security import generate_password_hash, check_password_hash


from flask_restful import Api

from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
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

        admin = user_datastore.find_user(email='admin@hospital.com')
        doctor = user_datastore.find_user(email='doctor@hospital.com')
        user = user_datastore.find_user(email='user@hospital.com')
        if not admin:
            user_datastore.create_user(
                username='admin',
                email='admin@hospital.com',
                password='admin123',
                active=True,
                roles=[admin_role, doctor_role, user_role]
            )
        if not doctor:
            user_datastore.create_user(
                username='doctor',
                email='doctor@hospital.com',
                password='doctor123',
                active=True,
                roles=[doctor_role, user_role]
            )
        if not user:
            user_datastore.create_user(
                username='user',
                email='user@hospital.com',
                password='user123',
                active=True,
                roles=[user_role]
            )


        for dept_data in [
            {'name': 'Cardiology', 'description': 'Heart and cardiovascular system'},
            {'name': 'Neurology', 'description': 'Brain and nervous system'},
            {'name': 'Orthopedics', 'description': 'Bones and muscles'},
            {'name': 'Pediatrics', 'description': 'Children healthcare'},
            {'name': 'Dermatology', 'description': 'Skin, hair, and nails'},
            {'name': 'General Medicine', 'description': 'General health issues'}
        ]:
            existing = Department.query.filter_by(name=dept_data['name']).first()
            if not existing:
                db.session.add(Department(**dept_data))



        db.session.commit()


from backend.authentication_apis import LoginAPI, LogoutAPI, RegisterAPI, CheckEmailAPI
api.add_resource(LoginAPI, '/login')
api.add_resource(LogoutAPI, '/logout')
api.add_resource(RegisterAPI, '/register')
api.add_resource(CheckEmailAPI, '/check-email')

from backend.crud_apis import CategoryCrudAPI
api.add_resource(CategoryCrudAPI, '/categories', '/categories/<int:category_id>')



@app.route("/start-task", methods=["GET"])
def start_task():
    task = example_task.delay()
    return jsonify({"task_id": task.id}), 202

@celery.on_after_finalize.connect 
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(),  # Every minutes 
        sheduler_task.s("1@example.com", "Test Subject", "Test Body"),
    )

if __name__ == "__main__":
    init_db(app) 
    app.run(debug = True)