from django.contrib.auth.views import LogoutView
from django.urls import path

from accounts.decorators import logout_required
from accounts.views import UserLoginView, UserProfileView, UserRegistrationView

app_name = 'accounts'

urlpatterns = [
    path('registration/', logout_required(UserRegistrationView.as_view()), name='registration'),
    path('login/', logout_required(UserLoginView.as_view()), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/<int:pk>/', UserProfileView.as_view(), name='profile'),
]
