from datetime import timedelta
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.views import (LoginView, PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from accounts.forms import (PwdResetForm, SetPwdForm, UserLoginForm,
                            UserProfileForm, UserRegistrationForm)
from accounts.models import EmailVerification, User

from humanize import naturaldelta


class UserRegistrationView(SuccessMessageMixin, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/registration.html'
    success_message = 'You have successfully registered!'
    success_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Special Recipe | Registration'
        return context


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('recipe:recipes')

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(1800)
        return super().form_valid(form)

    def form_invalid(self, form):
        if form.errors:
            messages.warning(self.request, 'Invalid username/email or password.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Special Recipe | Login'
        return context


class UserProfileView(SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    success_message = 'Profile updated successfully!'
    template_name = 'accounts/profile.html'

    def get_success_url(self):
        return reverse_lazy('accounts:profile', args={self.object.slug})

    def form_invalid(self, form):
        self.object.refresh_from_db()
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = f'Special Recipe | {self.object.username}\'s profile'
        return context


class SendVerificationEmailView(TemplateView):
    template_name = 'accounts/email/email_verification_sending_info.html'

    def get(self, request, *args, **kwargs):
        email = kwargs.get('email')
        user = get_object_or_404(User, email=email)
        if user != request.user:
            raise PermissionDenied
        valid_verifications = EmailVerification.objects.filter(user=user, expiration__gt=now()).order_by('-created')
        if user.is_verified:
            messages.warning(request, 'You have already verified your email.')
        elif valid_verifications.exists() and valid_verifications.first().created + timedelta(minutes=1) > now():
            seconds_left = naturaldelta(valid_verifications.first().created + timedelta(minutes=1) - now())
            messages.warning(request, f'Please wait {seconds_left} to resend the confirmation email.')
        else:
            expiration = now() + timedelta(hours=48)
            verification = EmailVerification.objects.create(code=uuid4(), user=user, expiration=expiration)
            verification.send_verification_email()
            messages.success(request, f'You\'re almost there! We send an email to {email}. '
                                      'Just click on the link in that email to complete your verification if '
                                      'you don\'t see it, you may need to check your spam folder.')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sending a verification email'
        return context


class EmailVerificationView(TemplateView):
    template_name = 'accounts/email/email_verification_complete.html'

    def get(self, request, *args, **kwargs):
        code = kwargs.get('code')
        email = kwargs.get('email')
        user = get_object_or_404(User, email=email)
        if user != request.user:
            raise PermissionDenied
        email_verification = get_object_or_404(EmailVerification, user=user, code=code)
        if user.is_verified:
            messages.warning(request, 'Your email has already been verified.')
        elif not email_verification.is_expired():
            user.is_verified = True
            user.save()
            messages.success(request, 'Your email address has been successfully verified.')
        else:
            messages.warning(request, 'The verification link has expired.')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Email verification'
        return context


class PwdResetView(SuccessMessageMixin, PasswordResetView):
    title = 'Special Recipe | Password reset'
    template_name = 'accounts/password/reset_password.html'
    form_class = PwdResetForm
    success_url = reverse_lazy('accounts:password_reset_done')
    success_message = 'We’ve emailed you instructions for setting your password, if an account exists with the email ' \
                      'you entered. You should receive them shortly. If you don’t receive an email, please make sure ' \
                      'you’ve entered the address you registered with, and check your spam folder.'


class PwdResetDoneView(PasswordResetDoneView):
    title = 'Special Recipe | Reset sent'
    template_name = 'accounts/password/password_reset_done.html'


class PwdResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    title = 'Special Recipe | New password creation'
    template_name = 'accounts/password/password_reset_confirm.html'
    form_class = SetPwdForm
    success_url = reverse_lazy('accounts:password_reset_complete')
    success_message = 'Your password has been set. You can now sign into your account with the new password.'


class PwdResetCompleteView(PasswordResetCompleteView):
    title = 'Special Recipe | Reset complete'
    template_name = 'accounts/password/password_reset_complete.html'
