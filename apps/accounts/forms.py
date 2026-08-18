import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import User


def normalize_rut(value):
    """Return the RUT body, removing formatting and an explicit check digit."""
    value = value.strip()
    match = re.fullmatch(r"([\d.]+)-[\dkK]", value)
    if match:
        return match.group(1).replace('.', '')
    return re.sub(r"\D", "", value)


def build_initial_password(first_name, rut):
    name = re.sub(r"[^A-Za-z0-9]", "", first_name or "Usuario")
    return f"{name.title()}-{rut}"


class UserCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].required = False
        self.fields['role'].initial = User.Role.USER

    class Meta:
        model = User
        fields = ('rut', 'first_name', 'last_name', 'email', 'role', 'is_active')
        labels = {
            'rut': 'RUT (sin dígito verificador)',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'role': 'Rol',
            'is_active': 'Usuario activo',
        }
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'azerta-input', 'placeholder': '12.345.678-5'}),
            'first_name': forms.TextInput(attrs={'class': 'azerta-input'}),
            'last_name': forms.TextInput(attrs={'class': 'azerta-input'}),
            'email': forms.EmailInput(attrs={'class': 'azerta-input'}),
            'role': forms.Select(attrs={'class': 'azerta-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'azerta-checkbox'}),
        }

    def clean_rut(self):
        rut = normalize_rut(self.cleaned_data['rut'])
        if not rut:
            raise forms.ValidationError('Ingrese un RUT válido.')
        return rut

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.rut
        user.is_staff = user.role in (User.Role.TI, User.Role.ADMIN)
        user.set_password(build_initial_password(user.first_name, user.rut))
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
        fields = ('rut', 'first_name', 'last_name', 'email', 'role', 'is_active')
        labels = UserCreateForm.Meta.labels
        widgets = UserCreateForm.Meta.widgets

    def clean_rut(self):
        rut = normalize_rut(self.cleaned_data['rut'])
        if not rut:
            raise forms.ValidationError('Ingrese un RUT válido.')
        return rut

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.rut
        user.is_staff = user.role in (User.Role.TI, User.Role.ADMIN)
        if self.cleaned_data.get('reset_password'):
            user.set_password(build_initial_password(user.first_name, user.rut))
        if commit:
            user.save()
        return user


class AzertaLoginForm(AuthenticationForm):
    """
    Azerta-styled authentication form.
    """
    username = forms.CharField(
        label="Ejecutivo",
        widget=forms.TextInput(attrs={
            'class': 'azerta-input',
            'placeholder': 'RUT del ejecutivo',
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
