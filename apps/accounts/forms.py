import random
import re
import unicodedata
from datetime import datetime

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import User


def generate_random_user_id():
    while True:
        value = str(random.randint(100, 999))
        if not User.objects.filter(username=value).exists():
            return value


def normalize_rut(value):
    """Return the RUT body, removing formatting and an explicit check digit."""
    value = value.strip()
    match = re.fullmatch(r"([\d.]+)-[\dkK]", value)
    if match:
        return match.group(1).replace('.', '')
    return re.sub(r"\D", "", value)


def _password_initial(value):
    cleaned = unicodedata.normalize('NFKD', (value or '')).encode('ascii', 'ignore').decode('ascii')
    cleaned = re.sub(r'[^A-Za-z]', '', cleaned)
    return cleaned[:1].upper() if cleaned else 'X'


def build_initial_password(first_name, last_name, creation_year=None):
    year = creation_year if creation_year is not None else datetime.now().year
    first_initial = _password_initial(first_name)
    last_initial = _password_initial(last_name) or first_initial
    return f"{first_initial}{last_initial}*{year}"


def build_username(first_name, last_name):
    first_initial = _password_initial(first_name)
    raw_last_name = (last_name or '').strip()
    if not raw_last_name:
        return first_initial.lower()
    cleaned_last_name = unicodedata.normalize('NFKD', raw_last_name)
    cleaned_last_name = cleaned_last_name.encode('ascii', 'ignore').decode('ascii')
    cleaned_last_name = cleaned_last_name.replace('Ñ', 'N').replace('ñ', 'n')
    cleaned_last_name = re.sub(r'[^A-Za-z]', '', cleaned_last_name)
    return f"{first_initial}{cleaned_last_name}".lower()


class UserCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].required = False
        self.fields['role'].initial = User.Role.USER

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'role', 'is_active')
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'role': 'Rol',
            'is_active': 'Usuario activo',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'azerta-input'}),
            'last_name': forms.TextInput(attrs={'class': 'azerta-input'}),
            'email': forms.EmailInput(attrs={'class': 'azerta-input'}),
            'role': forms.Select(attrs={'class': 'azerta-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'azerta-checkbox'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = build_username(user.first_name, user.last_name)
        if User.objects.filter(username=user.username).exclude(pk=user.pk).exists():
            suffix = 1
            candidate = user.username
            while User.objects.filter(username=candidate).exclude(pk=user.pk).exists():
                candidate = f"{user.username}{suffix}"
                suffix += 1
            user.username = candidate
        user.is_staff = user.role in (User.Role.TI, User.Role.ADMIN)
        user.set_password(build_initial_password(user.first_name, user.last_name, user.date_joined.year))
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    reset_password = forms.BooleanField(
        required=False,
        label='Restablecer contraseña al formato inicial',
        widget=forms.CheckboxInput(attrs={'class': 'azerta-checkbox'}),
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'role', 'is_active')
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'role': 'Rol',
            'is_active': 'Usuario activo',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'azerta-input'}),
            'last_name': forms.TextInput(attrs={'class': 'azerta-input'}),
            'email': forms.EmailInput(attrs={'class': 'azerta-input'}),
            'role': forms.Select(attrs={'class': 'azerta-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'azerta-checkbox'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if user.role == User.Role.ADMIN:
            user.username = user.username or 'admin'
        else:
            user.username = build_username(user.first_name, user.last_name)
            if User.objects.filter(username=user.username).exclude(pk=user.pk).exists():
                suffix = 1
                candidate = user.username
                while User.objects.filter(username=candidate).exclude(pk=user.pk).exists():
                    candidate = f"{user.username}{suffix}"
                    suffix += 1
                user.username = candidate
        user.is_staff = user.role in (User.Role.TI, User.Role.ADMIN)
        if self.cleaned_data.get('reset_password'):
            user.set_password(build_initial_password(user.first_name, user.last_name, user.date_joined.year))
        if commit:
            user.save()
        return user


class AzertaLoginForm(AuthenticationForm):
    """
    Azerta-styled authentication form.
    """
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            'class': 'azerta-input',
            'placeholder': 'Nombre de usuario',
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
