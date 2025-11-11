# Celery Configuration for Hospital Management System

broker_url = "redis://localhost:6379/0"
result_backend = "redis://localhost:6379/1"
timezone = "Asia/Kolkata"
broker_connection_retry_on_startup = True

# Task result expires after 1 hour
result_expires = 3600

# Task serialization
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']

# Celery Beat Schedule (for periodic tasks)
beat_schedule = {
    'send-daily-reminders': {
        'task': 'application.tasks.send_daily_reminders',
        'schedule': 3600.0,  # Run every hour (for testing, change to crontab for production)
        # For production: 'schedule': crontab(hour=8, minute=0),  # 8 AM daily
    },
    'send-monthly-reports': {
        'task': 'application.tasks.send_monthly_reports',
        'schedule': 86400.0,  # Run daily (for testing)
        # For production: 'schedule': crontab(day_of_month=1, hour=9, minute=0),  # 1st of month at 9 AM
    },
}