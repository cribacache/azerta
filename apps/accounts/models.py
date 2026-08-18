from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Add any extra fields here in the future.
    """
    class Role(models.TextChoices):
        USER = 'USUARIO', 'Usuario'
        TI = 'TI', 'TI'
        ADMIN = 'ADMIN', 'Administrador'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Rol',
    )
    onboarding_dismissed = models.BooleanField(
        default=False,
        verbose_name='No mostrar guía inicial',
    )
    rut = models.CharField(
        max_length=12,
        unique=True,
        null=True,
        blank=True,
        verbose_name="RUT sin dígito verificador",
        help_text="Se usa como nombre de usuario para iniciar sesión.",
    )
