from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.tickets.models import Ticket

from .forms import build_initial_password, build_username


class AzertaAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='azerta_user',
            email='usuario@azerta.cl',
            password='SecurePassword123!'
        )

    def test_login_page_renders_with_azerta_branding(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mesa de Soporte")
        self.assertContains(response, "Azerta")
        self.assertContains(response, "#FF0066")

    def test_successful_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'azerta_user',
            'password': 'SecurePassword123!',
            'remember_me': True,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_role_guide_can_be_dismissed_persistently(self):
        self.client.login(username='azerta_user', password='SecurePassword123!')
        dashboard = self.client.get(reverse('dashboard'))
        self.assertContains(dashboard, 'Guía rápida')
        response = self.client.post(reverse('dismiss_onboarding'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.onboarding_dismissed)
        self.assertNotContains(response, 'Guía rápida')

    def test_invalid_login_shows_error(self):
        response = self.client.post(reverse('login'), {
            'username': 'azerta_user',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Credenciales incorrectas")

    def test_logout_redirects_to_login(self):
        self.client.login(username='azerta_user', password='SecurePassword123!')
        response = self.client.post(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_staff_can_create_user_without_rut_and_initial_password(self):
        self.client.login(username='azerta_user', password='SecurePassword123!')
        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])
        response = self.client.post(reverse('user_create'), {
            'first_name': 'Ana',
            'last_name': 'Pérez',
            'email': 'ana@azerta.cl',
            'is_active': True,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        created = self.User.objects.filter(email='ana@azerta.cl').latest('id')
        self.assertEqual(created.username, 'aperez')
        self.assertTrue(created.check_password(build_initial_password('Ana', 'Pérez', created.date_joined.year)))

    def test_password_format_uses_initials_and_creation_year(self):
        self.assertEqual(build_initial_password('Ana', 'Pérez', 2026), 'AP*2026')
        self.assertEqual(build_initial_password('Juan', 'Carlos', 2024), 'JC*2024')

    def test_username_uses_first_letter_and_full_last_name(self):
        self.assertEqual(build_username('Ana', 'Pérez'), 'aperez')
        self.assertEqual(build_username('Juan', 'Carlos'), 'jcarlos')

    def test_regular_user_cannot_access_user_management(self):
        self.client.login(username='azerta_user', password='SecurePassword123!')
        response = self.client.get(reverse('user_list'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_regular_user_cannot_access_django_admin_by_url(self):
        self.client.login(username='azerta_user', password='SecurePassword123!')
        response = self.client.get('/admin/')
        self.assertRedirects(response, reverse('dashboard'))

    def test_ti_cannot_access_django_admin_by_url(self):
        ti = self.User.objects.create_user(
            username='ti_admin_route', password='SecurePassword123!',
            role=self.User.Role.TI, is_staff=True,
        )
        self.client.login(username=ti.username, password='SecurePassword123!')
        response = self.client.get('/admin/')
        self.assertRedirects(response, reverse('dashboard'))

    def test_admin_can_access_django_admin_by_url(self):
        admin_user = self.User.objects.create_superuser(
            username='real_admin', password='SecurePassword123!',
        )
        self.client.login(username=admin_user.username, password='SecurePassword123!')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_editing_user_keeps_support_history(self):
        self.user.is_staff = True
        self.user.rut = '12345678'
        self.user.save(update_fields=['is_staff', 'rut'])
        ticket = Ticket.objects.create(
            title='Historial',
            description='Solicitud previa',
            created_by=self.user,
        )
        self.client.login(username='azerta_user', password='SecurePassword123!')
        response = self.client.post(reverse('user_update', kwargs={'pk': self.user.pk}), {
            'rut': '12345678',
            'first_name': 'Carlos',
            'last_name': 'Actualizado',
            'email': 'nuevo@azerta.cl',
            'is_active': True,
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Ticket.objects.get(pk=ticket.pk).created_by_id, self.user.pk)
