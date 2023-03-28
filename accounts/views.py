from datetime import timedelta
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from humanize import naturaldelta

from accounts import forms as account_forms
from accounts.models import EmailVerification, User
from accounts.tasks import send_verification_email
from utils.uid import is_valid_uuid


class UserRegistrationView(SuccessMessageMixin, CreateView):
    model = User
    form_class = account_forms.UserRegistrationForm
    template_name = 'accounts/registration.html'
    success_message = 'You have successfully registered!'
    success_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Special Recipe | Registration'
        return context


class UserLoginView(auth_views.LoginView):
    form_class = account_forms.UserLoginForm
    template_name = 'accounts/login.html'

    def get_success_url(self):
        next_query = self.request.GET.get('next')
        if next_query:
            return next_query
        return reverse_lazy('accounts:profile', args={self.request.user.slug})

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
    form_class = account_forms.UserProfileForm
    success_message = 'Profile updated successfully!'
    template_name = 'accounts/profile/profile.html'

    def get_success_url(self):
        return reverse_lazy('accounts:profile', args=(self.object.slug,))

    def form_invalid(self, form):
        self.object.refresh_from_db()
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = f'Special Recipe | Profile - Account'
        return context


class UserProfilePasswordView(SuccessMessageMixin, auth_views.PasswordChangeView):
    template_name = 'accounts/profile/profile.html'
    title = 'Special Recipe | Profile - Password'
    form_class = account_forms.PasswordChangeForm
    success_message = 'Your password has been successfully updated!'

    def get_success_url(self):
        return reverse_lazy('accounts:profile-password', args={self.request.user.slug})


class SendVerificationEmailView(TemplateView):
    template_name = 'accounts/email/email_verification_done.html'

    def get(self, request, *args, **kwargs):
        email = kwargs.get('email')
        user = get_object_or_404(User, email=email)
        if user != request.user:
            raise Http404
        valid_verifications = EmailVerification.objects.filter(user=user, expiration__gt=now()).order_by('-created')
        if user.is_verified:
            messages.warning(request, 'You have already verified your email.')
        elif valid_verifications.exists() and valid_verifications.first().created + timedelta(minutes=1) > now():
            seconds_left = naturaldelta(valid_verifications.first().created + timedelta(minutes=1) - now())
            messages.warning(request, f'Please wait {seconds_left} to resend the confirmation email.')
        else:
            expiration = now() + timedelta(hours=48)
            verification = EmailVerification.objects.create(code=uuid4(), user=user, expiration=expiration)
            send_verification_email.delay(object_id=verification.id)
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
        if user != request.user or not is_valid_uuid(str(code)):
            raise Http404
        verification = get_object_or_404(EmailVerification, user=user, code=code)
        if user.is_verified:
            messages.warning(request, 'Your email has already been verified.')
        elif not verification.is_expired():
            user.is_verified = True
            user.save()
        else:
            messages.warning(request, 'The verification link has expired.')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Email verification'
        return context


class PasswordResetView(SuccessMessageMixin, auth_views.PasswordResetView):
    title = 'Special Recipe | Password reset'
    template_name = 'accounts/password/reset_password.html'
    subject_template_name = 'accounts/password/password_reset_subject.html'
    email_template_name = 'accounts/password/password_reset_email.html'
    form_class = account_forms.PasswordResetForm
    success_url = reverse_lazy('accounts:reset_password')
    success_message = 'We’ve emailed you instructions for setting your password, if an account exists with the email ' \
                      'you entered. You should receive them shortly. If you don’t receive an email, please make sure ' \
                      'you’ve entered the address you registered with, and check your spam folder.'


class PasswordResetConfirmView(SuccessMessageMixin, auth_views.PasswordResetConfirmView):
    template_name = 'accounts/password/password_reset_confirm.html'
    form_class = account_forms.SetPasswordForm
    success_url = reverse_lazy('accounts:login')
    success_message = 'Your password has been set. You can now sign into your account with the new password.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Special Recipe | Password reset'
        return context
