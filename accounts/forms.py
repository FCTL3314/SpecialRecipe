from django import forms
from django.contrib.auth import forms as auth_forms
from django.template.loader import render_to_string

from accounts.models import User
from accounts.tasks import send_email


class UserRegistrationForm(auth_forms.UserCreationForm):
    username = forms.CharField(min_length=4, widget=forms.TextInput(attrs={
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
        fields = ('username', 'password')


class UserProfileForm(auth_forms.UserChangeForm):
    username = forms.CharField(min_length=4, widget=forms.TextInput(attrs={
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

    def save(self, commit=True):
        old_email = self.initial.get('email')
        new_email = self.cleaned_data.get('email')
        if old_email != new_email:
            self.instance.is_verified = False
            self.instance.save()
        return super().save(commit=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'image')


class PwdChangeForm(auth_forms.PasswordChangeForm):
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

    def clean_new_password2(self):
        new_password1 = self.cleaned_data['new_password1']
        new_password2 = self.cleaned_data['new_password2']
        if new_password1 == new_password2 and self.user.check_password(new_password2):
            raise forms.ValidationError('The new password must be different from the old one.')
        return super().clean_new_password2()

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')


class PwdResetForm(auth_forms.PasswordResetForm):
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
            send_email.delay(subject=subject, message=message, emails_list=[to_email])

    class Meta:
        model = User
        fields = ('email',)


class SetPwdForm(auth_forms.SetPasswordForm):
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
