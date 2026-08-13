from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


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
        self.assertContains(response, "Acceso a Plataforma")
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
