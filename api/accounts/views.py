from django.conf import settings
from django.shortcuts import get_object_or_404
from djoser import email as email_views
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import EmailVerification, User
from accounts.tasks import send_verification_email
from api.accounts.serializers import EmailVerificationSerializer
from utils.uid import is_valid_uuid


class PasswordResetEmail(email_views.PasswordResetEmail):
    template_name = 'accounts/password/password_reset_email.html'
    subject_template_name = 'accounts/password/password_reset_subject.html'


class SendVerificationEmailCreateAPIView(CreateAPIView):
    queryset = EmailVerification.objects.all()
    serializer_class = EmailVerificationSerializer
    permission_classes = (IsAuthenticated,)
    sending_interval = settings.EMAIL_SEND_INTERVAL_SECONDS

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)

        if not user.is_request_user_matching(request):
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        elif user.is_verified:
            return Response({'detail': 'Already verified.'}, status=status.HTTP_400_BAD_REQUEST)

        seconds_since_last_email = user.seconds_since_last_email_verification()

        if seconds_since_last_email < self.sending_interval:
            seconds_left = self.sending_interval - seconds_since_last_email
            response = {
                'detail': 'Messages per minute limit reached.',
                'seconds_left': seconds_left,
            }
            return Response(response, status=status.HTTP_429_TOO_MANY_REQUESTS)
        else:
            verification = user.create_email_verification()
            send_verification_email.delay(object_id=verification.id)
            serializer = self.get_serializer(verification, partial=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class EmailVerificationUpdateAPIView(UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        code = request.data.get('code')
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)

        if not user.is_request_user_matching(request) or not is_valid_uuid(str(code)):
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        elif user.is_verified:
            return Response({'detail': 'Already verified.'}, status=status.HTTP_400_BAD_REQUEST)

        verification = get_object_or_404(EmailVerification, user=user, code=code)
        if not verification.is_expired():
            user.verify()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'Link was expired.'}, status=status.HTTP_410_GONE)
