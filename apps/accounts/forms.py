from django import forms
from django.contrib.auth.forms import AuthenticationForm


class AzertaLoginForm(AuthenticationForm):
    """
    Azerta-styled authentication form.
    """
    username = forms.CharField(
        label="Usuario o Email",
        widget=forms.TextInput(attrs={
            'class': 'azerta-input',
            'placeholder': 'nombre@azerta.cl o usuario',
            'autocomplete': 'username',
            'autofocus': True,
            'id': 'id_username',
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'azerta-input',
            'placeholder': '••••••••••••',
            'autocomplete': 'current-password',
            'id': 'id_password',
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        label="Recordar sesión",
        widget=forms.CheckboxInput(attrs={
            'class': 'azerta-checkbox',
            'id': 'id_remember_me',
        })
    )
