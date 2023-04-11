from celery import shared_task
from django.conf import settings

from accounts.models import EmailVerification, User
from common.mail import convert_html_to_email_message


@shared_task
def send_verification_email(object_id):
    verification = EmailVerification.objects.get(id=object_id)
    verification.send_verification_email(protocol=settings.PROTOCOL)


@shared_task
def send_email(subject_template_name, email_template_name, to_email, context=None):
    context['user'] = User.objects.get(id=context['user'])
    msg = convert_html_to_email_message(subject_template_name, email_template_name, [to_email], context)
    msg.send()
