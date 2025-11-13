import time
from celery import shared_task
from .mail import send_email


@shared_task(ignore_results=False, name = "This is a example task")
def example_task():
    time.sleep(10)
    print("example task")
    return {
        "message":"task completed"
        }, 200


@shared_task(ignore_results=False, name = "this is the example of sending email")
def sheduler_task(to_email, subject, body):
    send_email(to_email, subject, body)
    print("sheduler task")
    return {
        "message":"sheduler task completed"
        }, 200    
