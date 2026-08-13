from django.db import models
from django.conf import settings


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
        on_delete=models.CASCADE,
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

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Ticket de Soporte"
        verbose_name_plural = "Tickets de Soporte"

    def __str__(self):
        return f"#{self.id} - {self.title} ({self.get_status_display()})"
