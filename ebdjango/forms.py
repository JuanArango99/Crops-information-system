from django.contrib.auth.forms import PasswordResetForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User

class EmailValidationOnForgotPassword(PasswordResetForm):

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = ("No existe un usuario con esa dirección de correo.")
            self.add_error('email', msg)
        return email

class MyAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': "Por favor ingrese un nombre de usuario y una contraseña válidos.",
    }

    def __init__(self, *args, **kwargs):
        super(MyAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['password'].label = 'Contraseña'

class MySetPasswordForm(SetPasswordForm):
    error_messages = {
        'password_mismatch': "Las contraseñas no coinciden.",
    }

    def __init__(self, *args, **kwargs):
        super(MySetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].label = 'Contraseña'
        self.fields['new_password2'].label = 'Confirmar Contraseña'
   

    