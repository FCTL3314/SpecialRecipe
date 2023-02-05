from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path

from accounts.decorators import logout_required
from accounts.views import (EmailVerificationView, PwdResetCompleteView,
                            PwdResetConfirmView, PwdResetDoneView,
                            PwdResetView, SendVerificationEmailView,
                            UserLoginView, UserProfileView,
                            UserRegistrationView)

app_name = 'accounts'

urlpatterns = [
    path('registration/', logout_required(UserRegistrationView.as_view()), name='registration'),
    path('login/', logout_required(UserLoginView.as_view()), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('<slug:slug>/', UserProfileView.as_view(), name='profile'),
    path(
        'verification/send/<str:email>/',
        login_required(SendVerificationEmailView.as_view()),
        name='send-verification-email'
    ),
    path('verify/<str:email>/<uuid:code>/', login_required(EmailVerificationView.as_view()), name='email-verification'),
    path('password_reset/', logout_required(PwdResetView.as_view()), name='reset_password'),
    path('password_reset/done/', logout_required(PwdResetDoneView.as_view()), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', logout_required(PwdResetConfirmView.as_view()), name='password_reset_confirm'),
    path(
        'reset/done/',
        logout_required(PwdResetCompleteView.as_view(template_name='accounts/password/password_reset_complete.html')),
        name='password_reset_complete'
    ),
]
