import logging

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now

from accounts.tasks import send_email


logger = logging.getLogger('mailings')


class User(AbstractUser):
    image = models.ImageField(upload_to='user_images', null=True, blank=True)
    email = models.EmailField(db_index=True, unique=True, max_length=254)
    is_verified = models.BooleanField(default=False)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.username)
        return super().save()

    def clean(self):
        self.email = self.email.lower()
        return super().clean()

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'


class EmailVerification(models.Model):
    code = models.UUIDField(unique=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    def send_verification_email(self, subject_template_name='accounts/email/email_verification_subject.html',
                                html_email_template_name='accounts/email/email_verification_email.html',
                                use_https=False):
        link = reverse('accounts:email-verification', kwargs={'email': self.user.email, 'code': self.code})

        context = {
            'user': self.user,
            'protocol': 'https' if use_https else 'http',
            'verification_link': settings.DOMAIN_NAME + link,
        }

        raw_subject = render_to_string(subject_template_name)
        subject = ''.join(raw_subject.splitlines())
        message = render_to_string(html_email_template_name, context)
        emails_list = [self.user.email]
        send_email.delay(subject=subject, message=message, emails_list=emails_list)
        logger.info(f'Request to send a verification email to {self.user.email}')

    def is_expired(self):
        return True if self.expiration < now() else False

    def __str__(self):
        return f'Email verification for {self.user.email}'
