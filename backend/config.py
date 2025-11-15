# class Config:
#     SECRET_KEY = 'your_secret_key_here'
#     SQLALCHEMY_DATABASE_URI = 'sqlite:///HMS.db'

#     SECURITY_PASSWORD_SALT = 'your_password_salt_here'
#     SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authorization'


class Config:
    SECRET_KEY = 'your_secret_key_here_change_in_production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///HMS.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Security configuration
    SECURITY_PASSWORD_SALT = 'your_password_salt_here_change_in_production'
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
    SECURITY_PASSWORD_HASH = 'bcrypt'
    
    # Disable some Flask-Security features for API usage
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_TRACKABLE = False
    
    # Allow sessions without HTTPS in development
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    