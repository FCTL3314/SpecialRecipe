from datetime import timedelta
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from accounts.forms import UserLoginForm, UserProfileForm, UserRegistrationForm
from accounts.models import EmailVerification, User


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
        response = super().form_valid(form)
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(1800)
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if form and form.errors:
            messages.warning(self.request, 'Invalid username/email or password.')
        return response

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
        return reverse_lazy('accounts:profile', args={self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        form = kwargs.get('form')
        if form and form.errors:
            context['user'] = User.objects.get(id=self.object.id)
        context['title'] = f'Special Recipe | {self.object.username}\'s profile'
        return context
    
    
class SendVerificationEmailView(TemplateView):
    template_name = 'accounts/email_verification/sending_information.html'

    def get(self, request, *args, **kwargs):
        email = kwargs.get('email')
        user = User.objects.get(email=email)
        valid_verifications = EmailVerification.objects.filter(user=user, expiration__gt=now())
        if user.is_verified:
            messages.warning(request, 'You have already verified your email.')
        elif valid_verifications:
            messages.warning(request, 'The last sent email has not expired yet, use it to verify your email address.')
        else:
            expiration = now() + timedelta(hours=48)
            verification = EmailVerification.objects.create(code=uuid4(), user=user, expiration=expiration)
            verification.send_verification_email()
            messages.success(request, f'You\'re almost there! We send an email to {email}. '
                                      'Just click on the link in that email to complete your verification if '
                                      'you don\'t see it, you may need to check your spam folder.')
        return super().get(request, *args, **kwargs)


class EmailVerificationView(TemplateView):
    template_name = 'accounts/email_verification/complete.html'

    def get(self, request, *args, **kwargs):
        code = kwargs.get('code')
        email = kwargs.get('email')
        user = User.objects.get(email=email)
        email_verification = get_object_or_404(EmailVerification, user=user, code=code)
        if user.is_verified:
            messages.warning(request, 'Your email has already been verified.')
        elif not email_verification.is_expired():
            user.is_verified = True
            user.save()
            messages.success(request, 'Your email address has been successfully verified.')
        else:
            messages.warning(request, 'An unknown error occurred while verifying your email, please try again later.')
        return super().get(request, *args, **kwargs)
