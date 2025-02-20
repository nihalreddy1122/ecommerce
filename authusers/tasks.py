from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now
from .models import TemporaryUser
from datetime import timedelta
from django.template.loader import render_to_string

@shared_task
def delete_expired_temp_users():
    """Delete TemporaryUser records older than 5 minutes."""
    expired_users = TemporaryUser.objects.filter(created_at__lt=now() - timedelta(minutes=1))
    count = expired_users.count()
    expired_users.delete()
    return f"Deleted {count} expired TemporaryUser entries."

@shared_task
def send_email_task(subject, message, from_email, recipient_list, html_message=None):
    """Asynchronous task to send an email."""
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipient_list,
        html_message=html_message,
    )
