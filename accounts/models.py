import logging
from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now

from accounts.managers import EmailVerificationManager
from common.mail import convert_html_to_email_message

logger = logging.getLogger('mailings')


class User(AbstractUser):
    image = models.ImageField(upload_to='user_images', null=True, blank=True)
    email = models.EmailField(db_index=True, unique=True, max_length=254)
    is_verified = models.BooleanField(default=False)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.username)
        return super().save()

    def clean(self):
        self.email = self.email.lower()
        return super().clean()

    def seconds_since_last_email_verification(self):
        valid_verifications = EmailVerification.objects.valid_user_verifications(user=self).order_by('-created')
        if valid_verifications.exists():
            elapsed_time = now() - valid_verifications.first().created
        else:
            elapsed_time = timedelta(seconds=settings.EMAIL_SEND_INTERVAL_SECONDS)
        return elapsed_time.seconds

    def create_email_verification(self):
        expiration = now() + timedelta(hours=settings.EMAIL_EXPIRATION_HOURS)
        return EmailVerification.objects.create(code=uuid4(), user=self, expiration=expiration)

    def is_request_user_matching(self, request):
        return self == request.user

    def verify(self):
        self.is_verified = True
        self.save()


class EmailVerification(models.Model):
    code = models.UUIDField(unique=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    objects = EmailVerificationManager()

    def __str__(self):
        return f'Email verification for {self.user.email}'

    def send_verification_email(self, subject_template_name='accounts/email/email_verification_subject.html',
                                html_email_template_name='accounts/email/email_verification_email.html',
                                protocol='http'):
        link = reverse('accounts:email-verification', kwargs={'email': self.user.email, 'code': self.code})

        context = {
            'user': self.user,
            'protocol': protocol,
            'verification_link': settings.DOMAIN_NAME + link,
        }
        msg = convert_html_to_email_message(subject_template_name, html_email_template_name, [self.user.email], context)
        msg.send()

        logger.info(f'Request to send a verification email to {self.user.email}')

    def is_expired(self):
        return self.expiration < now()
