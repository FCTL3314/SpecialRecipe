from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

from accounts.models import User
from accounts.forms import UserRegistrationForm


class UserRegistrationView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/registration.html'
    success_url = reverse_lazy('recipe:recipes')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Special Recipe - Registration'
        return context
