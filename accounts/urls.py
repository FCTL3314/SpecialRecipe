from django.urls import path
from django.contrib.auth.views import LogoutView

from accounts.views import UserRegistrationView, UserLoginView, UserProfileView
from accounts.decorators import logout_required


app_name = 'accounts'

urlpatterns = [
    path('registration/', logout_required(UserRegistrationView.as_view()), name='registration'),
    path('login/', logout_required(UserLoginView.as_view()), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/<int:pk>/', UserProfileView.as_view(), name='profile'),
]
