from django.urls import path
from django.contrib.auth.views import LogoutView

from accounts.views import UserRegistrationView, UserLoginView


app_name = 'accounts'

urlpatterns = [
    path('registration/', UserRegistrationView.as_view(), name='registration'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
