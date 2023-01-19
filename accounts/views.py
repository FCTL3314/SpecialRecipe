from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from accounts.models import User
from accounts.forms import UserRegistrationForm, UserLoginForm, UserProfileForm


class UserRegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/registration.html'
    success_url = reverse_lazy('accounts:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Special Recipe - Registration'
        return context


class UserLoginView(LoginView):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('recipe:recipes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Special Recipe - Login'
        return context


class UserProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'

    def get_success_url(self):
        return reverse_lazy('accounts:profile', args={self.request.user.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = f'Special Recipe - {self.request.user.username}\'s profile'
        return context
