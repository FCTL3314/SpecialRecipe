from django.utils.text import slugify
from rest_framework import serializers

from accounts.models import EmailVerification, User


class UserSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False)

    def save(self, **kwargs):
        username = self.initial_data.get('username')
        slug = self.initial_data.get('slug')
        if username and not slug:
            self.instance.slug = slugify(username)
        return super().save(**kwargs)

    class Meta:
        model = User
        fields = ('id', 'image', 'username', 'first_name', 'last_name', 'email', 'slug')


class EmailVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailVerification
        fields = ('id', 'created', 'expiration', 'user')
