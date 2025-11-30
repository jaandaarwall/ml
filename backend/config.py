class Config:
    SECRET_KEY = 'your_secret_key_here_change_in_production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///HMS.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Security configuration
    SECURITY_PASSWORD_SALT = 'your_password_salt_here_change_in_production'
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
    # SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha256'


 # Use RedisCache backend
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_URL = 'redis://localhost:6379/2'
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX = 'hms_api_'