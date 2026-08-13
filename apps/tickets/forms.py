from django import forms
from .models import Ticket


class TicketCreateForm(forms.ModelForm):
    """Form for regular users to create a support ticket."""
    class Meta:
        model = Ticket
        fields = ['title', 'category', 'priority', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'azerta-input',
                'placeholder': 'Ej. Problema con acceso a VPN / Solicitud de software',
                'required': True,
                'id': 'id_ticket_title',
            }),
            'category': forms.Select(attrs={
                'class': 'azerta-select',
                'id': 'id_ticket_category',
            }),
            'priority': forms.Select(attrs={
                'class': 'azerta-select',
                'id': 'id_ticket_priority',
            }),
            'description': forms.Textarea(attrs={
                'class': 'azerta-textarea',
                'placeholder': 'Describa detalladamente el problema o requerimiento...',
                'rows': 4,
                'required': True,
                'id': 'id_ticket_description',
            }),
        }


class TicketAdminUpdateForm(forms.ModelForm):
    """Form for administrators to update ticket status and add resolution notes."""
    class Meta:
        model = Ticket
        fields = ['status', 'priority', 'assigned_to', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'azerta-select',
                'id': 'id_admin_status',
            }),
            'priority': forms.Select(attrs={
                'class': 'azerta-select',
                'id': 'id_admin_priority',
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'azerta-select',
                'id': 'id_admin_assigned_to',
            }),
            'admin_notes': forms.Textarea(attrs={
                'class': 'azerta-textarea',
                'placeholder': 'Escriba notas internas de atención, pasos realizados o motivo de resolución...',
                'rows': 3,
                'id': 'id_admin_notes',
            }),
        }
