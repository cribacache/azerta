from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import View, DetailView
from django.contrib import messages
from django.db.models import Count, Q
from .models import Ticket
from .forms import TicketCreateForm, TicketAdminUpdateForm


class DashboardView(LoginRequiredMixin, View):
    """
    Main portal dashboard:
    - Displays all tickets & metrics for Admin / Staff.
    - Displays user's tickets & creation form for Regular users.
    """
    def get(self, request):
        user = request.user
        form = TicketCreateForm()

        if user.is_staff or user.is_superuser:
            status_filter = request.GET.get('status', '')
            tickets_qs = Ticket.objects.all()
            if status_filter:
                tickets_qs = tickets_qs.filter(status=status_filter)

            total_count = Ticket.objects.count()
            pending_count = Ticket.objects.filter(status=Ticket.Status.PENDING).count()
            in_progress_count = Ticket.objects.filter(status=Ticket.Status.IN_PROGRESS).count()
            resolved_count = Ticket.objects.filter(status=Ticket.Status.RESOLVED).count()

            context = {
                'is_admin': True,
                'tickets': tickets_qs,
                'status_filter': status_filter,
                'stats': {
                    'total': total_count,
                    'pending': pending_count,
                    'in_progress': in_progress_count,
                    'resolved': resolved_count,
                },
                'form': form,
            }
        else:
            user_tickets = Ticket.objects.filter(created_by=user)
            context = {
                'is_admin': False,
                'tickets': user_tickets,
                'stats': {
                    'total': user_tickets.count(),
                    'pending': user_tickets.filter(status=Ticket.Status.PENDING).count(),
                    'in_progress': user_tickets.filter(status=Ticket.Status.IN_PROGRESS).count(),
                    'resolved': user_tickets.filter(status=Ticket.Status.RESOLVED).count(),
                },
                'form': form,
            }

        return render(request, 'tickets/dashboard.html', context)

    def post(self, request):
        """Handle new ticket creation from dashboard."""
        form = TicketCreateForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            messages.success(request, f"Ticket #{ticket.id} '{ticket.title}' creado exitosamente.")
            return redirect('dashboard')
        else:
            messages.error(request, "Hubo un error al crear el ticket. Revise los campos.")
            return self.get(request)


class TicketDetailView(LoginRequiredMixin, View):
    """
    Detailed ticket view with admin update controls.
    """
    def get(self, request, pk):
        if request.user.is_staff or request.user.is_superuser:
            ticket = get_object_or_404(Ticket, pk=pk)
        else:
            ticket = get_object_or_404(Ticket, pk=pk, created_by=request.user)

        admin_form = TicketAdminUpdateForm(instance=ticket) if (request.user.is_staff or request.user.is_superuser) else None

        return render(request, 'tickets/ticket_detail.html', {
            'ticket': ticket,
            'admin_form': admin_form,
            'is_admin': request.user.is_staff or request.user.is_superuser,
        })

    def post(self, request, pk):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "No tienes permisos para modificar este ticket.")
            return redirect('dashboard')

        ticket = get_object_or_404(Ticket, pk=pk)
        admin_form = TicketAdminUpdateForm(request.POST, instance=ticket)
        if admin_form.is_valid():
            admin_form.save()
            messages.success(request, f"Ticket #{ticket.id} actualizado correctamente.")
            return redirect('ticket_detail', pk=ticket.id)
        else:
            messages.error(request, "Error al actualizar el ticket.")
            return render(request, 'tickets/ticket_detail.html', {
                'ticket': ticket,
                'admin_form': admin_form,
                'is_admin': True,
            })
