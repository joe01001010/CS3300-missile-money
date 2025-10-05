from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'joe_test_user',
            'password': 'idklmao123123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_home_page_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_about_page_status_code(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_page_status_code(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_profile_page_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username='joe_test_user', password='idklmao123123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'joe_test_user2',
            'password1': 'idklmao123123',
            'password2': 'idklmao123123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
        self.assertTrue(User.objects.filter(username='joe_test_user').exists())

    def test_user_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'joe_test_user',
            'password': 'idklmao123123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/', response.url)

    def test_user_logout(self):
        self.client.login(username='joe_test_user', password='idklmao123123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))