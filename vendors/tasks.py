from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string

@shared_task
def send_vendor_activation_email_task(user_email, user_first_name):
    """Asynchronous task to send vendor activation email."""
    subject = "Your Vendor Account is Active!"
    plain_message = f"Congratulations {user_first_name}! Your vendor account on HIDDEN STORES is now active."
    html_message = render_to_string('emails/vendor_activation_email.html', {
        'user': {'first_name': user_first_name},
        'site_url': 'https://hiddenstores.com',  # Replace with actual site URL
    })
    send_mail(
        subject=subject,
        message=plain_message,
        from_email="no-reply@hiddenstores.com",
        recipient_list=[user_email],
        html_message=html_message,
    )
