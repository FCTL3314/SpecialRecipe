from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.urls import path

from accounts import views as account_view
from accounts.decorators import logout_required

app_name = 'accounts'

urlpatterns = [
    path('registration/', logout_required(account_view.UserRegistrationView.as_view()), name='registration'),
    path('login/', logout_required(account_view.UserLoginView.as_view()), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('user/<slug:slug>/', account_view.UserProfileView.as_view(), name='profile'),
    path('user/<slug:slug>/email/', account_view.UserProfileEmailView.as_view(), name='profile-email'),
    path('user/<slug:slug>/password/', account_view.UserProfilePasswordView.as_view(), name='profile-password'),

    path('verification/send/<str:email>/', login_required(account_view.SendVerificationEmailView.as_view()),
         name='send-verification-email'),
    path('verify/<str:email>/<uuid:code>/', login_required(account_view.EmailVerificationView.as_view()),
         name='email-verification'),

    path('password_reset/', logout_required(account_view.PasswordResetView.as_view()), name='reset_password'),
    path('reset/<uidb64>/<token>/', logout_required(account_view.PasswordResetConfirmView.as_view()),
         name='password_reset_confirm'),
]
