from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_email(subject, message, emails_list, html_message=None):
    send_mail(
        subject=subject,
        message=message,
        html_message=html_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=emails_list,
        fail_silently=False,
    )
