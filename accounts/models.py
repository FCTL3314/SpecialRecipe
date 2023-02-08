from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now


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

    def send_verification_email(self):
        link = reverse('accounts:email-verification', kwargs={'email': self.user.email, 'code': self.code})
        verification_link = settings.DOMAIN_NAME + link

        subject = f'Special Recipe | Email verification'
        message = f'Hello, to verify your email address, follow the link below:\n\n{verification_link}'
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user.email],
            fail_silently=False,
        )

    def is_expired(self):
        return True if self.expiration < now() else False

    def __str__(self):
        return f'Email verification for {self.user.email}'
