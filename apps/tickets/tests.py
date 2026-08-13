from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Ticket


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
