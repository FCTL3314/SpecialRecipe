from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.timezone import now
from djoser import email as email_views
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import EmailVerification, User
from accounts.tasks import send_email, send_verification_email
from api.serializers.accounts import EmailVerificationSerializer
from utils.uid import is_valid_uuid


class PasswordResetEmail(email_views.PasswordResetEmail):
    template_name = 'accounts/password/password_reset_email.html'
    subject_template_name = 'accounts/password/password_reset_subject.html'
    use_https = False if settings.DEBUG else True

    def send(self, to, *args, **kwargs):
        context = self.get_context_data()
        context['protocol'] = 'https' if self.use_https else 'http'

        raw_subject = render_to_string(self.subject_template_name)
        subject = ''.join(raw_subject.splitlines())
        message = render_to_string(self.template_name, context)

        send_email.delay(subject=subject, message=message, recipient_list=[to])


class SendVerificationEmailCreateAPIView(CreateAPIView):
    queryset = EmailVerification.objects.all()
    serializer_class = EmailVerificationSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)
        if user != request.user:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        valid_verifications = EmailVerification.objects.filter(user=user, expiration__gt=now()).order_by('-created')
        if user.is_verified:
            return Response({'detail': 'Already verified.'}, status=status.HTTP_400_BAD_REQUEST)
        elif valid_verifications.exists() and valid_verifications.first().created + timedelta(minutes=1) > now():
            time_left = valid_verifications.first().created + timedelta(minutes=1) - now()
            response = {
                'detail': 'Messages per minute limit reached.',
                'seconds_left': time_left.seconds,
            }
            return Response(response, status=status.HTTP_429_TOO_MANY_REQUESTS)
        else:
            data = {
                'code': uuid4(),
                'created': now(),
                'expiration': now() + timedelta(hours=48),
                'user': request.user.id,
            }
            serializer = self.get_serializer(data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            send_verification_email.delay(object_id=serializer.instance.id)
            response = serializer.data
            del response['code']
            return Response(response, status=status.HTTP_201_CREATED)


class EmailVerificationUpdateAPIView(UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        code = request.data.get('code')
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)
        if user != request.user or not is_valid_uuid(str(code)):
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        verification = EmailVerification.objects.filter(user=user, code=code)
        if user.is_verified:
            return Response({'detail': 'Already verified.'}, status=status.HTTP_400_BAD_REQUEST)
        elif verification.exists() and not verification.first().is_expired():
            user.is_verified = True
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'Link was expired.'}, status=status.HTTP_410_GONE)
