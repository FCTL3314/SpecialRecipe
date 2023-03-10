import logging

from django import forms
from django.contrib.auth import forms as auth_forms
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.text import slugify

from accounts.models import User
from accounts.tasks import send_email

mailings_logger = logging.getLogger('mailings')
accounts_logger = logging.getLogger('accounts')


class UserRegistrationForm(auth_forms.UserCreationForm):
    username = forms.CharField(min_length=4, max_length=32, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Username',
    }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Email',
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Password',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password',
    }))

    def save(self, commit=True):
        username = self.data.get('username')
        accounts_logger.info(f'User {username} has registered.')
        return super().save(commit=commit)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('A user with that username already exists.')
        return username

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UserLoginForm(auth_forms.AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Username or Email',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Password',
    }))
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input',
    }))

    class Meta:
        model = User
        fields = ('username', 'password', 'remember_me')


class UserProfileForm(auth_forms.UserChangeForm):
    username = forms.CharField(min_length=4, max_length=32, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
    }))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'Alex',
    }))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'type': 'text',
        'placeholder': 'Miller',
    }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
    }))
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control',
        'type': 'file',
        'aria-label': 'Upload',
    }))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username.lower() != self.instance.username.lower() and User.objects.filter(username__iexact=username
                                                                                      ).exists():
            raise ValidationError('A user with that username already exists.')
        return username

    def save(self, commit=True):
        username = self.cleaned_data.get('username')
        old_email = self.initial.get('email')
        new_email = self.cleaned_data.get('email')
        if old_email.lower() != new_email.lower():
            self.instance.is_verified = False
            self.instance.save()
        if username:
            self.instance.slug = slugify(username)
        return super().save(commit=commit)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'image')


class PasswordChangeForm(auth_forms.PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your old password',
    }))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your new password',
    }))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter new password confirmation',
    }))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(user, *args, **kwargs)

    def clean(self):
        new_password1 = self.cleaned_data['new_password1']
        new_password2 = self.cleaned_data['new_password2']
        if new_password1 == new_password2 and self.user.check_password(new_password2):
            raise forms.ValidationError('The new password must be different from the old one.')
        return super().clean()

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')


class PasswordResetForm(auth_forms.PasswordResetForm):
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter Email',
    }))

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        raw_subject = render_to_string(subject_template_name)
        subject = ''.join(raw_subject.splitlines())
        message = render_to_string(email_template_name, context)
        if html_email_template_name is not None:
            html_message = render_to_string(html_email_template_name, context)
            send_email.delay(subject=subject, message=message, emails_list=[to_email], html_message=html_message)
        else:
            send_email.delay(subject=subject, message=message, recipient_list=[to_email])
        mailings_logger.info(f'Request to send a password reset email to {to_email}')

    class Meta:
        model = User
        fields = ('email',)


class SetPasswordForm(auth_forms.SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter new password',
    }))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm new password',
    }))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(user, *args, **kwargs)

    def clean_new_password2(self):
        new_password = self.cleaned_data['new_password1']
        if self.user.check_password(new_password):
            raise forms.ValidationError('The new password must be different from the old one.')
        return super().clean_new_password2()

    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')
