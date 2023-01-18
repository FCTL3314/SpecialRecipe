from django.urls import path

from accounts.views import UserRegistrationView


app_name = 'accounts'

urlpatterns = [
    path('registration/', UserRegistrationView.as_view(), name='registration'),
]
