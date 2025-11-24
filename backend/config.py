class Config:
    SECRET_KEY = 'your_secret_key_here_change_in_production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///HMS.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Security configuration
    SECURITY_PASSWORD_SALT = 'your_password_salt_here_change_in_production'
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
    # SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha256'

    
    # Disable some Flask-Security features for API usage
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_TRACKABLE = False
    
    # Allow sessions without HTTPS in development
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # -------------------------
    # Redis Cache Configuration
    # -------------------------
    # Use RedisCache backend
    CACHE_TYPE = 'RedisCache'
    # Connect to local Redis on standard port, using DB 2 (0 and 1 often used by Celery)
    CACHE_REDIS_URL = 'redis://localhost:6379/2'
    # Default timeout in seconds (5 minutes)
    CACHE_DEFAULT_TIMEOUT = 300
    # Prefix for all keys to avoid collisions
    CACHE_KEY_PREFIX = 'hms_api_'