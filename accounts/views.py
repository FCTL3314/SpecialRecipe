from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from accounts import forms as account_forms
from accounts.models import EmailVerification, User
from accounts.tasks import send_verification_email
from common.views import LogoutRequiredMixin, TitleMixin
from utils.uid import is_valid_uuid


class UserRegistrationView(LogoutRequiredMixin, SuccessMessageMixin, TitleMixin, CreateView):
    model = User
    form_class = account_forms.UserRegistrationForm
    template_name = 'accounts/registration.html'
    success_message = 'You have successfully registered!'
    success_url = reverse_lazy('accounts:login')
    title = 'Special Recipe | Registration'


class UserLoginView(LogoutRequiredMixin, TitleMixin, auth_views.LoginView):
    form_class = account_forms.UserLoginForm
    template_name = 'accounts/login.html'
    title = 'Special Recipe | Registration'

    def get(self, request, *args, **kwargs):
        request.session['before_login_url'] = request.META.get('HTTP_REFERER')
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        next_query = self.request.session.get('before_login_url')
        return next_query if next_query else reverse_lazy('accounts:profile', args={self.request.user.slug})

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(1800)
        return super().form_valid(form)

    def form_invalid(self, form):
        if form.errors:
            messages.warning(self.request, 'The entered data is incorrect, please try again.')
        return super().form_invalid(form)


class LogoutView(auth_views.LogoutView):

    def get_next_page(self):
        referer = self.request.META.get('HTTP_REFERER')
        if referer:
            return referer
        return super().get_next_page()


class UserProfileView(SuccessMessageMixin, TitleMixin, UpdateView):
    model = User
    form_class = account_forms.UserProfileForm
    success_message = 'Profile updated successfully!'
    template_name = 'accounts/profile/profile.html'
    title = 'Special Recipe | Account'

    def get_success_url(self):
        return reverse_lazy('accounts:profile', args=(self.object.slug,))

    def form_invalid(self, form):
        self.object.refresh_from_db()
        return super().form_invalid(form)


class UserProfilePasswordView(SuccessMessageMixin, auth_views.PasswordChangeView):
    template_name = 'accounts/profile/profile.html'
    title = 'Special Recipe | Password'
    form_class = account_forms.PasswordChangeForm
    success_message = 'Your password has been successfully updated!'

    def get_success_url(self):
        return reverse_lazy('accounts:profile-password', args={self.request.user.slug})


class UserProfileEmailView(SuccessMessageMixin, auth_views.PasswordChangeView):
    template_name = 'accounts/profile/profile.html'
    title = 'Special Recipe | Email'
    form_class = account_forms.EmailChangeForm
    success_message = 'Your email has been successfully changed!'

    def get_success_url(self):
        return reverse_lazy('accounts:profile-email', args={self.request.user.slug})


class SendVerificationEmailView(LoginRequiredMixin, TitleMixin, TemplateView):
    template_name = 'accounts/email/email_verification_done.html'
    title = 'Special Recipe | Send Verification'
    sending_interval = settings.EMAIL_SEND_INTERVAL_SECONDS

    def get(self, request, *args, **kwargs):
        email = kwargs.get('email')
        user = get_object_or_404(User, email=email)

        if not user.is_request_user_matching(request):
            raise Http404

        seconds_since_last_email = user.seconds_since_last_email_verification()

        if user.is_verified:
            messages.warning(request, 'You have already verified your email.')
        elif seconds_since_last_email < self.sending_interval:
            seconds_left = self.sending_interval - seconds_since_last_email
            messages.warning(request, f'Please wait {seconds_left} to resend the confirmation email.')
        else:
            verification = user.create_email_verification()
            send_verification_email.delay(object_id=verification.id)
        return super().get(request, *args, **kwargs)


class EmailVerificationView(TemplateView):
    template_name = 'accounts/email/email_verification_complete.html'

    def get(self, request, *args, **kwargs):
        code = kwargs.get('code')
        email = kwargs.get('email')
        user = get_object_or_404(User, email=email)

        if not user.is_request_user_matching(request) or not is_valid_uuid(str(code)):
            raise Http404

        verification = get_object_or_404(EmailVerification, user=user, code=code)

        if user.is_verified:
            messages.warning(request, 'Your email has already been verified.')
        elif not verification.is_expired():
            user.verify()
        else:
            messages.warning(request, 'The verification link has expired.')
        return super().get(request, *args, **kwargs)


class PasswordResetView(LogoutRequiredMixin, SuccessMessageMixin, auth_views.PasswordResetView):
    title = 'Special Recipe | Password Reset'
    template_name = 'accounts/password/reset_password.html'
    subject_template_name = 'accounts/password/password_reset_subject.html'
    email_template_name = 'accounts/password/password_reset_email.html'
    form_class = account_forms.PasswordResetForm
    success_url = reverse_lazy('accounts:reset_password')
    success_message = 'We’ve emailed you instructions for setting your password, if an account exists with the email ' \
                      'you entered. You should receive them shortly. If you don’t receive an email, please make sure ' \
                      'you’ve entered the address you registered with, and check your spam folder.'


class PasswordResetConfirmView(LogoutRequiredMixin, SuccessMessageMixin, TitleMixin,
                               auth_views.PasswordResetConfirmView):
    title = 'Special Recipe | Password Reset'
    template_name = 'accounts/password/password_reset_confirm.html'
    form_class = account_forms.SetPasswordForm
    success_url = reverse_lazy('accounts:login')
    success_message = 'Your password has been set. You can now sign into your account with the new password.'
