from datetime import timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone


class Ticket(models.Model):
    """
    Support ticket model for Azerta helpdesk.
    """
    class Priority(models.TextChoices):
        LOW = 'BAJA', 'Baja'
        MEDIUM = 'MEDIA', 'Media'
        HIGH = 'ALTA', 'Alta'
        URGENT = 'CRITICA', 'Crítica / Urgente'

    class Status(models.TextChoices):
        PENDING = 'PENDIENTE', 'Pendiente'
        IN_PROGRESS = 'EN_PROCESO', 'En Proceso'
        RESOLVED = 'RESUELTO', 'Resuelto'
        CLOSED = 'CERRADO', 'Cerrado'

    class Category(models.TextChoices):
        TECH = 'TI', 'Soporte Técnico & Hardware'
        SOFTWARE = 'SOFTWARE', 'Software & Plataformas'
        NETWORK = 'REDES', 'Redes & Conectividad'
        COMMUNICATION = 'COMUNICACION', 'Comunicaciones & Prensa'
        ACCESS = 'ACCESOS', 'Accesos & Contraseñas'
        OTHER = 'OTRO', 'Otro Requerimiento'

    title = models.CharField(max_length=200, verbose_name="Asunto / Título")
    description = models.TextField(verbose_name="Descripción detallada del requerimiento")
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.TECH,
        verbose_name="Categoría"
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name="Prioridad"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Estado"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        verbose_name="Creado por"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name="Asignado a"
    )
    admin_notes = models.TextField(
        blank=True,
        verbose_name="Notas de resolución / TI"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Inicio de atención")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Fin de atención")

    @property
    def resolution_seconds(self):
        if not self.started_at:
            return None
        end = self.resolved_at or timezone.now()
        return max(0, int((end - self.started_at).total_seconds()))

    @property
    def resolution_duration(self):
        seconds = self.resolution_seconds
        if seconds is None:
            return ''
        return str(timedelta(seconds=seconds))

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Ticket de Soporte"
        verbose_name_plural = "Tickets de Soporte"

    def __str__(self):
        return f"#{self.id} - {self.title} ({self.get_status_display()})"


class TicketResponse(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Incidencia',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ticket_responses',
        verbose_name='Ingresado por',
    )
    message = models.TextField(verbose_name='Respuesta')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de ingreso')

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Respuesta de incidencia'
        verbose_name_plural = 'Respuestas de incidencias'
