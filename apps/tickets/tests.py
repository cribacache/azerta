from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Ticket, TicketResponse


class SupportTicketsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.admin_user = self.User.objects.create_superuser(
            username='admin_test',
            email='admin@azerta.cl',
            password='testpassword'
        )
        self.regular_user = self.User.objects.create_user(
            username='regular_test',
            email='regular@azerta.cl',
            password='testpassword'
        )
        self.ti_user = self.User.objects.create_user(
            username='ti_test', password='testpassword', role='TI', is_staff=True,
        )
        self.ticket = Ticket.objects.create(
            title='Test Ticket Issue',
            description='Detailed problem description',
            category=Ticket.Category.TECH,
            priority=Ticket.Priority.HIGH,
            status=Ticket.Status.PENDING,
            created_by=self.regular_user
        )

    def test_root_redirects_unauthenticated_user_to_login(self):
        response = self.client.get('/')
        self.assertRedirects(response, reverse('login'))

    def test_regular_user_dashboard_view(self):
        self.client.login(username='regular_test', password='testpassword')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Ticket Issue')
        self.assertContains(response, 'Nuevo Ticket de Soporte')

    def test_regular_user_can_create_ticket(self):
        self.client.login(username='regular_test', password='testpassword')
        response = self.client.post(reverse('dashboard'), {
            'title': 'New Printer Issue',
            'category': Ticket.Category.TECH,
            'priority': Ticket.Priority.MEDIUM,
            'description': 'Cannot connect to 4th floor printer.',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Ticket.objects.filter(title='New Printer Issue').exists())

    def test_admin_can_update_ticket_status(self):
        self.client.login(username='admin_test', password='testpassword')
        response = self.client.post(reverse('ticket_detail', kwargs={'pk': self.ticket.id}), {
            'status': Ticket.Status.RESOLVED,
            'priority': Ticket.Priority.HIGH,
            'admin_notes': 'Issue was solved by rebooting router.',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.RESOLVED)
        self.assertEqual(self.ticket.admin_notes, 'Issue was solved by rebooting router.')

    def test_regular_ticket_is_assigned_to_available_ti(self):
        self.client.login(username='regular_test', password='testpassword')
        response = self.client.post(reverse('dashboard'), {
            'title': 'Assigned ticket', 'category': Ticket.Category.TECH,
            'priority': Ticket.Priority.MEDIUM, 'description': 'Needs TI help.',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        created = Ticket.objects.get(title='Assigned ticket')
        self.assertEqual(created.assigned_to, self.ti_user)

    def test_ti_can_start_assigned_ticket_and_timer(self):
        self.ticket.assigned_to = self.ti_user
        self.ticket.save(update_fields=['assigned_to'])
        self.client.login(username='ti_test', password='testpassword')
        response = self.client.post(reverse('start_ticket', kwargs={'pk': self.ticket.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.IN_PROGRESS)
        self.assertIsNotNone(self.ticket.started_at)

    def test_ti_cannot_view_unassigned_user_ticket(self):
        self.client.login(username='ti_test', password='testpassword')
        response = self.client.get(reverse('ticket_detail', kwargs={'pk': self.ticket.pk}), follow=True)
        self.assertRedirects(response, reverse('dashboard'))

    def test_admin_can_create_manual_incident_without_requester(self):
        self.client.login(username='admin_test', password='testpassword')
        response = self.client.post(reverse('dashboard'), {
            'title': 'Manual incident', 'category': Ticket.Category.NETWORK,
            'priority': Ticket.Priority.HIGH, 'description': 'Detected by monitoring.',
            'created_by': '', 'assigned_to': str(self.ti_user.pk),
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        manual = Ticket.objects.get(title='Manual incident')
        self.assertIsNone(manual.created_by)
        self.assertEqual(manual.assigned_to, self.ti_user)

    def test_report_page_is_available(self):
        self.client.login(username='admin_test', password='testpassword')
        response = self.client.get(reverse('ticket_report'), {'period': 'month'})
        self.assertEqual(response.status_code, 200)

    def test_ticket_response_records_author_and_timestamp(self):
        self.client.login(username='admin_test', password='testpassword')
        response = self.client.post(reverse('ticket_detail', kwargs={'pk': self.ticket.pk}), {
            'status': Ticket.Status.IN_PROGRESS,
            'priority': Ticket.Priority.HIGH,
            'assigned_to': str(self.ti_user.pk),
            'admin_notes': '',
            'response': 'Se inició la revisión de la incidencia.',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        entry = TicketResponse.objects.get(ticket=self.ticket)
        self.assertEqual(entry.author, self.admin_user)
        self.assertEqual(entry.message, 'Se inició la revisión de la incidencia.')
        self.assertIsNotNone(entry.created_at)
