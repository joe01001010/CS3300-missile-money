from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core import mail
import datetime

class AuthenticationTests(TestCase):
    def setUp(self):
        """
        This function will set up the test client and create a test user
        There is no return value for this function
        """
        self.client = Client()
        self.user_data = {
            'username': 'joe_test_user',
            'password': 'idklmao123123'
        }
        self.user = User.objects.create_user(**self.user_data)


    def test_home_page_status_code(self):
        """
        This function will attempt to access the home page without logging in
        This should return a 200 status code
        There is no return value for this function
        """
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)


    def test_about_page_status_code(self):
        """
        This function will attempt to access the about page without logging in
        This should return a 200 status code
        There is no return value for this function
        """
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)


    def test_dashboard_page_status_code(self):
        """
        This function will attempt to access the dashboard page without logging in
        This should redirect to the login page and return a 302 status code
        There is no return value for this function
        """
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)


    def test_profile_page_requires_login(self):
        """
        This function will attempt to access the profile page without logging in
        This should redirect to the login page and return a 302 status code
        There is no return value for this function
        """
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username='joe_test_user', password='idklmao123123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)


    def test_user_registration(self):
        """
        This function will register a new user and then redirect to the login page
        This should return a 302 status code and redirect to the login page
        There is no return value for this function
        """
        response = self.client.post(reverse('register'), {
            'username': 'joe_test_user2',
            'password1': 'idklmao123123',
            'password2': 'idklmao123123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
        self.assertTrue(User.objects.filter(username='joe_test_user').exists())


    def test_user_login(self):
        """
        This function will log in as the test user and then redirect to the dashboard page
        This should return a 302 status code and redirect to the dashboard page
        There is no return value for this function
        """
        response = self.client.post(reverse('login'), {
            'username': 'joe_test_user',
            'password': 'idklmao123123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/', response.url)


    def test_user_logout(self):
        """
        This function will log in as the test user and then logout
        This should redirect to the home page and return a 302 status code
        There is no return value for this function
        """
        self.client.login(username='joe_test_user', password='idklmao123123')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))


    def test_auto_logout_after_inactivity(self):
        """
        This function will log in as the test user and then accesss the dashboard page
        This will then simulate the user being inactive instead of waitin the entire 15 minutes
        This should trigger logout and then redirect to the login page
        There is no return value for this function
        """
        self.client.login(username='joe_test_user', password='idklmao123123')

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        session = self.client.session

        now = datetime.datetime.now()
        expired_time = now - datetime.timedelta(seconds=getattr(settings, 'AUTO_LOGOUT_DELAY', 15 * 60) + 10)
        session['last_activity'] = expired_time.isoformat()
        session.save()

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)


    def test_feedback_submission_sends_email(self):
        """
        This function will use the locmem email backend for testing and store the email message in memory
        This function will ensure the user is redirected back to the page they clicked the feedback button from
        This also checks to make sure the test email was sent
        This also checks to make sure the email message is formatted properly with subject, recipient, content
        """
        with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
            feedback_data = {
                'email': 'testuser@example.com',
                'message': 'This is a test feedback message.'
            }

            response = self.client.post(reverse('submit_feedback'), data=feedback_data, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(mail.outbox), 1)
            sent_email = mail.outbox[0]

            self.assertIn('Missile Money - User Feedback', sent_email.subject)
            self.assertIn('This is a test feedback message.', sent_email.body)
            self.assertIn('testuser@example.com', sent_email.body)
            self.assertEqual(sent_email.to, ['support@missilemoney.com'])