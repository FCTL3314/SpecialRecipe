from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

from accounts.models import User
from accounts.forms import UserRegistrationForm, UserLoginForm, UserProfileForm


class UserRegistrationView(SuccessMessageMixin, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/registration.html'
    success_message = 'You have successfully registered!'
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
        context['title'] = f'Special Recipe - {self.object.username}\'s profile'
        return context
