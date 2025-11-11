from flask import Flask
from .config import Config
from .database import db
from .models import User, Roles
from flask_security import Security, SQLAlchemyUserDatastore
from flask_caching import Cache
from flask_cors import CORS
from .celery_init import init_celery

user_datastore = SQLAlchemyUserDatastore(db, User, Roles)
cache = Cache()
security = Security()

def create_app():
    app = Flask(__name__, template_folder='../frontend/templates')
    app.config.from_object(Config)

    db.init_app(app)
    cache.init_app(app)
    CORS(app)
    security.init_app(app, user_datastore)
    init_celery(app)

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
