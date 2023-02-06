from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path

from accounts.decorators import logout_required
from accounts.views import (EmailVerificationView, PwdChangeDoneView,
                            PwdChangeView, PwdResetCompleteView,
                            PwdResetConfirmView, PwdResetDoneView,
                            PwdResetView, SendVerificationEmailView,
                            UserLoginView, UserProfileView,
                            UserRegistrationView)

app_name = 'accounts'

urlpatterns = [
    path('registration/', logout_required(UserRegistrationView.as_view()), name='registration'),
    path('login/', logout_required(UserLoginView.as_view()), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/<slug:slug>/', UserProfileView.as_view(), name='profile'),

    path('verification/send/<str:email>/', login_required(SendVerificationEmailView.as_view()),
         name='send-verification-email'),
    path('verify/<str:email>/<uuid:code>/', login_required(EmailVerificationView.as_view()), name='email-verification'),

    path('password_change/', PwdChangeView.as_view(), name='password_change'),
    path('password_change/done/', PwdChangeDoneView.as_view(), name='password_change_done'),

    path('password_reset/', logout_required(PwdResetView.as_view()), name='reset_password'),
    path('password_reset/done/', logout_required(PwdResetDoneView.as_view()), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', logout_required(PwdResetConfirmView.as_view()), name='password_reset_confirm'),
    path('reset/done/', logout_required(PwdResetCompleteView.as_view()), name='password_reset_complete'),
]
