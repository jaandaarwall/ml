class Config:
    SECRET_KEY = 'this-is-a-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///hospital_management.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECURITY_PASSWORD_SALT = 'this-is-a-password-salt'
    SECURITY_PASSWORD_HASH = 'bcrypt'
    WTF_CSRF_ENABLED = False
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
    SECURITY_TOKEN_MAX_AGE = 86400  # 24 hours
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 2
    CACHE_DEFAULT_TIMEOUT = 300
