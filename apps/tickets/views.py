import random
from datetime import datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import View

from .forms import TicketAdminCreateForm, TicketAdminUpdateForm, TicketCreateForm
from .models import Ticket, TicketResponse


def is_admin(user):
    return user.is_superuser or user.role == 'ADMIN' or (user.is_staff and user.role != 'TI')


def is_ti(user):
    return user.role == 'TI'


def available_ti():
    from django.contrib.auth import get_user_model

    User = get_user_model()
    busy_ti_ids = Ticket.objects.filter(
        assigned_to__role='TI', status=Ticket.Status.IN_PROGRESS
    ).values_list('assigned_to_id', flat=True)
    return User.objects.filter(role='TI', is_active=True).exclude(id__in=busy_ti_ids)


def assign_available_ti(ticket):
    candidates = list(available_ti())
    if candidates:
        ticket.assigned_to = random.choice(candidates)


class DashboardView(LoginRequiredMixin, View):
    """Daily operational queue; historical analysis lives in reports."""
    def get(self, request):
        today = timezone.localdate()
        today_start = timezone.make_aware(datetime.combine(today, time.min))
        tomorrow_start = today_start + timedelta(days=1)
        base_qs = Ticket.objects.filter(
            created_at__gte=today_start, created_at__lt=tomorrow_start
        ).select_related('created_by', 'assigned_to')

        if is_admin(request.user):
            tickets = base_qs
            admin_form = TicketAdminCreateForm()
        elif is_ti(request.user):
            tickets = base_qs.filter(assigned_to__role='TI')
            if request.GET.get('assigned') == 'me':
                tickets = tickets.filter(assigned_to=request.user)
            admin_form = None
        else:
            tickets = base_qs.filter(created_by=request.user)
            admin_form = None

        context = {
            'is_admin': is_admin(request.user),
            'is_ti': is_ti(request.user),
            'tickets': tickets,
            'today': today,
            'assigned_filter': request.GET.get('assigned', ''),
            'stats': {
                'total': tickets.count(),
                'pending': tickets.filter(status=Ticket.Status.PENDING).count(),
                'in_progress': tickets.filter(status=Ticket.Status.IN_PROGRESS).count(),
                'resolved': tickets.filter(status=Ticket.Status.RESOLVED).count(),
            },
            'form': TicketCreateForm(),
            'admin_form': admin_form,
        }
        return render(request, 'tickets/dashboard.html', context)

    def post(self, request):
        if is_admin(request.user):
            form = TicketAdminCreateForm(request.POST)
            if form.is_valid():
                ticket = form.save()
                messages.success(request, f'Incidencia #{ticket.id} creada manualmente.')
                return redirect('dashboard')
            messages.error(request, 'Hubo un error al crear la incidencia.')
            return self.get(request)

        form = TicketCreateForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            assign_available_ti(ticket)
            ticket.save()
            messages.success(request, f'Ticket #{ticket.id} creado exitosamente.')
            return redirect('dashboard')
        messages.error(request, 'Hubo un error al crear el ticket. Revise los campos.')
        return self.get(request)


class StartTicketView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if not is_ti(request.user):
            messages.error(request, 'Solo un usuario TI puede iniciar una tarea.')
            return redirect('dashboard')
        with transaction.atomic():
            ticket = get_object_or_404(
                Ticket.objects.select_for_update(), pk=pk, assigned_to=request.user
            )
            if ticket.status == Ticket.Status.PENDING:
                ticket.status = Ticket.Status.IN_PROGRESS
                ticket.started_at = timezone.now()
                ticket.save(update_fields=['status', 'started_at', 'updated_at'])
                messages.success(request, f'La tarea #{ticket.id} está en curso y el cronómetro comenzó.')
        return redirect('ticket_detail', pk=pk)


class TicketDetailView(LoginRequiredMixin, View):
    def can_view(self, request, ticket):
        return (
            is_admin(request.user)
            or (is_ti(request.user) and ticket.assigned_to and ticket.assigned_to.role == 'TI')
            or ticket.created_by_id == request.user.id
        )

    def get(self, request, pk):
        ticket = get_object_or_404(Ticket.objects.prefetch_related('responses__author'), pk=pk)
        if not self.can_view(request, ticket):
            messages.error(request, 'No tienes permisos para ver esta solicitud.')
            return redirect('dashboard')
        admin_form = TicketAdminUpdateForm(instance=ticket) if is_admin(request.user) else None
        return render(request, 'tickets/ticket_detail.html', {
            'ticket': ticket,
            'admin_form': admin_form,
            'is_admin': is_admin(request.user),
            'is_ti': is_ti(request.user),
        })

    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)
        if is_admin(request.user):
            form = TicketAdminUpdateForm(request.POST, instance=ticket)
            if form.is_valid():
                ticket = form.save(commit=False)
                if ticket.status in (Ticket.Status.RESOLVED, Ticket.Status.CLOSED) and not ticket.resolved_at:
                    ticket.resolved_at = timezone.now()
                ticket.save()
                response_text = form.cleaned_data.get('response', '').strip()
                if response_text:
                    TicketResponse.objects.create(
                        ticket=ticket, author=request.user, message=response_text
                    )
                messages.success(request, f'Ticket #{ticket.id} actualizado correctamente.')
                return redirect('ticket_detail', pk=pk)
        elif is_ti(request.user) and ticket.assigned_to_id == request.user.id:
            new_status = request.POST.get('status')
            if new_status in Ticket.Status.values:
                ticket.status = new_status
                if new_status in (Ticket.Status.RESOLVED, Ticket.Status.CLOSED):
                    ticket.resolved_at = timezone.now()
                ticket.admin_notes = request.POST.get('admin_notes', ticket.admin_notes)
                ticket.save(update_fields=['status', 'resolved_at', 'admin_notes', 'updated_at'])
                response_text = request.POST.get('response', '').strip()
                if response_text:
                    TicketResponse.objects.create(
                        ticket=ticket, author=request.user, message=response_text
                    )
                messages.success(request, f'Ticket #{ticket.id} actualizado correctamente.')
                return redirect('ticket_detail', pk=pk)
        messages.error(request, 'No tienes permisos para modificar este ticket.')
        return redirect('dashboard')


class TicketReportView(LoginRequiredMixin, View):
    def get(self, request):
        period = request.GET.get('period', 'week')
        today = timezone.localdate()
        if period == 'month':
            start_date = today.replace(day=1)
        elif period == 'day':
            start_date = today
        else:
            start_date = today - timedelta(days=today.weekday())
            period = 'week'
        start = timezone.make_aware(datetime.combine(start_date, time.min))
        visible = Ticket.objects.filter(
            created_at__gte=start, created_at__lte=timezone.now()
        )
        if is_admin(request.user):
            pass
        elif is_ti(request.user):
            visible = visible.filter(assigned_to__role='TI')
        else:
            visible = visible.filter(created_by=request.user)
        durations = [ticket.resolution_seconds for ticket in visible if ticket.resolution_seconds is not None]
        summary = visible.aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status=Ticket.Status.PENDING)),
            in_progress=Count('id', filter=Q(status=Ticket.Status.IN_PROGRESS)),
            resolved=Count('id', filter=Q(status__in=[Ticket.Status.RESOLVED, Ticket.Status.CLOSED])),
        )
        summary['average_seconds'] = int(sum(durations) / len(durations)) if durations else None
        return render(request, 'tickets/report.html', {
            'tickets': visible.select_related('created_by', 'assigned_to'),
            'summary': summary,
            'period': period,
            'start_date': start_date,
        })
