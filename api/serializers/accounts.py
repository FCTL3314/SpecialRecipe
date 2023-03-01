from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import EmailVerification, User


class UpdateUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(min_length=4, max_length=32)

    def validate_username(self, username):
        if username != self.instance.username and User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError('A user with that username already exists.')
        return username

    class Meta:
        model = User
        fields = ('id', 'image', 'username', 'first_name', 'last_name', 'email')


class ChangePasswordSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    old_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        password1 = attrs.get('password1')
        password2 = attrs.get('password2')
        if password1 != password2:
            raise serializers.ValidationError('Passwords do not match.')
        elif self.instance.check_password(password2):
            raise serializers.ValidationError('The new password must be different from the old one.')
        return attrs

    def validate_old_password(self, old_password):
        request = self.context.get('request')
        user = request.user
        if not user.check_password(old_password):
            raise serializers.ValidationError('Old password is not correct.')
        return old_password

    def update(self, instance, validated_data):
        password = validated_data.get('password1')
        instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('id', 'password1', 'password2', 'old_password')


class EmailVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailVerification
        fields = ('id', 'code', 'created', 'expiration', 'user')
