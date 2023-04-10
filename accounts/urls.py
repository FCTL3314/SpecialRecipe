from django.urls import path

from accounts import views as account_view

app_name = 'accounts'

urlpatterns = [
    path('registration/', account_view.UserRegistrationView.as_view(), name='registration'),
    path('login/', account_view.UserLoginView.as_view(), name='login'),
    path('logout/', account_view.LogoutView.as_view(), name='logout'),

    path('user/<slug:slug>/', account_view.UserProfileView.as_view(), name='profile'),
    path('user/<slug:slug>/email/', account_view.UserProfileEmailView.as_view(), name='profile-email'),
    path('user/<slug:slug>/password/', account_view.UserProfilePasswordView.as_view(), name='profile-password'),

    path('verification/send/<str:email>/', account_view.SendVerificationEmailView.as_view(),
         name='send-verification-email'),
    path('verify/<str:email>/<uuid:code>/', account_view.EmailVerificationView.as_view(),
         name='email-verification'),

    path('password_reset/', account_view.PasswordResetView.as_view(), name='reset_password'),
    path('reset/<uidb64>/<token>/', account_view.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
]
