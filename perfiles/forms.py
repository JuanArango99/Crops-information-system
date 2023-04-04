from django import forms
from .models import Perfil
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.forms import  TextInput, EmailInput, FileInput

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto']

        widgets = {
            'foto':FileInput(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['foto'].widget.clear_checkbox_label = 'Limpiar'
        self.fields['foto'].widget.initial_text = "Actual"
        self.fields['foto'].widget.input_text = "Cambiar a"        

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name']
        labels = {
            'username': _('Nombre de Usuario'),
            'email': _('Correo'),
            'first_name': _('Nombres'),
            'last_name': _('Apellidos'),
        }
        help_texts = {
            'username': _('Requerido. 150 caracteres o menos. Letras, Dígitos y @/./+/-/_ solamente.'),
        }
        widgets = {
            'username': TextInput(attrs={
                'class': "form-control", 
                'style': 'font-family: "Roboto", sans-serif;background: #0be11b26;width: 100%;border: 0;margin: 0 0 15px;padding: 15px;box-sizing: border-box;font-size: 14px; ',
                'placeholder': 'Nombre de Usuario'
                }),
            'email': EmailInput(attrs={
                'class': "form-control", 
                'style': 'font-family: "Roboto", sans-serif;outline: 0;background: #0be11b26;width: 100%;border: 0;margin: 0 0 15px;padding: 15px;box-sizing: border-box;font-size: 14px; ',
                'placeholder': 'Correo'
                }),
            'first_name': TextInput(attrs={
                'class': "form-control", 
                'style': 'font-family: "Roboto", sans-serif;outline: 0;background: #0be11b26;width: 100%;border: 0;margin: 0 0 15px;padding: 15px;box-sizing: border-box;font-size: 14px; ',
                'placeholder': 'Nombre(s)'
                }),
            'last_name': TextInput(attrs={
                'class': "form-control", 
                'style': 'font-family: "Roboto", sans-serif;outline: 0;background: #0be11b26;width: 100%;border: 0;margin: 0 0 15px;padding: 15px;box-sizing: border-box;font-size: 14px; ',
                'placeholder': 'Apellido(s)'
                }),
        }

class MyUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo")
    first_name = forms.CharField(max_length=30, label="Nombre")
    last_name = forms.CharField(max_length=30, label="Apellido")
    is_staff = forms.BooleanField(required=False, label="¿Es Admininstrador?")

    error_messages = {
        'password_mismatch': "Las contraseñas no coinciden.",
    }

    def __init__(self, *args, **kwargs):
        super(MyUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar Contraseña'

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2','is_staff')
        labels = {'username': _('Nombre de Usuario'),
                    }
        help_texts = {
            'username': _('Requerido. 150 caracteres o menos. Letras, Dígitos y @/./+/-/_ solamente.'),
            'password1': {

            },
            'password2': _('Ingrese la contraseña anterior, para verificar.'),
        }
        error_messages = {
            'username': {
                'unique': 'Ya existe un usuario con ese nombre.',
            },
        }

    def save(self, commit=True):
        user = super(MyUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.is_staff = self.cleaned_data['is_staff']
            user.save()
        return user

class MyChangePasswordForm(PasswordChangeForm):
    error_messages = {
        **SetPasswordForm.error_messages,
        "password_incorrect": _(
            "Su contraseña anterior es incorrecta, por favor, digitela nuevamente."
        ),
    }

    def __init__(self, *args, **kwargs):
        super(MyChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Contraseña Actual'
        self.fields['new_password1'].label = 'Contraseña Nueva'
        self.fields['new_password2'].label = 'Confirmar Contraseña'