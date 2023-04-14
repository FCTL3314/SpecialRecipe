from django.db import models
from django.utils.timezone import now


class EmailVerificationManager(models.Manager):

    def get_valid_user_verifications(self, user):
        return self.filter(user=user, expiration__gt=now())
