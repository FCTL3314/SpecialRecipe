from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from accounts.models import EmailVerification


@shared_task
def send_verification_email(object_id):
    verification = EmailVerification.objects.get(id=object_id)
    verification.send_verification_email(use_https=False if settings.DEBUG else True)


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
