from flask import Flask
from application.models import User, Roles
from application.config import LocalDevelopmentConfig
from flask_security import Security, SQLAlchemyUserDatastore
from werkzeug.security import generate_password_hash
from application.resources import init_api
from application.celery_init import celery_init_app
from celery.schedules import crontab
from application.cache import cache
from application.database import db
import uuid

def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    init_api(app)
    cache.init_app(app)
    datastore = SQLAlchemyUserDatastore(db, User, Roles)
    app.security = Security(app, datastore)
    with app.app_context():
        db.create_all()
        app.security.datastore.find_or_create_role(name="admin", description="Superuser of app")
        app.security.datastore.find_or_create_role(name="doctor", description="A doctor in the hospital")
        app.security.datastore.find_or_create_role(name="patient", description="A patient in the hospital")
        db.session.commit()
        if not app.security.datastore.find_user(email="admin@hms.com"):
            app.security.datastore.create_user(
                email="admin@hms.com",
                password=generate_password_hash("admin"),
                roles=['admin'],
                fs_uniquifier=str(uuid.uuid4())
            )
            db.session.commit()
    return app

app = create_app()
celery = celery_init_app(app)
celery.autodiscover_tasks(['application.tasks'])

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=8, minute=0),
        'application.tasks.send_daily_reminders',
    )
    sender.add_periodic_task(
        crontab(day_of_month=1, hour=0, minute=0),
        'application.tasks.generate_monthly_report',
    )

# Import routes after app creation to avoid circular import
with app.app_context():
    from application import routes

if __name__ == "__main__":
    app.run(debug=True)
