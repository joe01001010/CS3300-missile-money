from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core import mail
from main.models import Transaction
from decimal import Decimal
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
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)


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
            self.assertEqual(sent_email.to, ['support@missile-money.com'])


    def test_dashboard_transactions_by_month(self):
        """
        This function will login with the test user
        This function will create 2 transactions for 2 different months
        This function will ensure the total amoutn of money is correct
        This funciton will ensure the monthly totals are correct
        """
        self.client.login(username='joe_test_user', password='idklmao123123')

        Transaction.objects.create(user=self.user, type='income', amount=1000, date=datetime.date(2025, 10, 1))
        Transaction.objects.create(user=self.user, type='expense', amount=200, date=datetime.date(2025, 10, 15))
        Transaction.objects.create(user=self.user, type='income', amount=500, date=datetime.date(2025, 9, 10))
        Transaction.objects.create(user=self.user, type='expense', amount=100, date=datetime.date(2025, 9, 20))

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

        total_balance = response.context['total_balance']
        monthly_income = response.context['monthly_income']
        monthly_expenses = response.context['monthly_expenses']

        self.assertEqual(total_balance, 1200)
        self.assertEqual(monthly_income, 1500)
        self.assertEqual(monthly_expenses, 300)

class TransactionEditDeleteTestCase(TestCase):
    """
    Test cases for editing and deleting transactions
    """
    
    def setUp(self):
        """
        Set up test user and transactions before each test
        """
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test transactions
        self.income_transaction = Transaction.objects.create(
            user=self.user,
            type='income',
            amount=Decimal('2000.00'),
            description='Test Income'
        )
        
        self.expense_transaction = Transaction.objects.create(
            user=self.user,
            type='expense',
            amount=Decimal('500.00'),
            description='Test Expense'
        )
        
        # Set up test client
        self.client = Client()
    
    def test_edit_transaction_page_loads(self):
        """
        Test that the edit transaction page loads successfully
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('edit_transaction', args=[self.income_transaction.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Transaction')
    
    def test_edit_transaction_updates_data(self):
        """
        Test that editing a transaction actually updates the data
        """
        self.client.login(username='testuser', password='testpass123')
        
        # Edit the transaction
        response = self.client.post(
            reverse('edit_transaction', args=[self.income_transaction.id]),
            {
                'type': 'income',
                'amount': '3000.00',
                'description': 'Updated Income'
            }
        )
        
        # Check redirect to dashboard
        self.assertEqual(response.status_code, 302)
        
        # Verify the transaction was updated
        updated_transaction = Transaction.objects.get(id=self.income_transaction.id)
        self.assertEqual(updated_transaction.amount, Decimal('3000.00'))
        self.assertEqual(updated_transaction.description, 'Updated Income')
    
    def test_delete_transaction_page_loads(self):
        """
        Test that the delete confirmation page loads successfully
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('delete_transaction', args=[self.expense_transaction.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete Transaction')
    
    def test_delete_transaction_removes_data(self):
        """
        Test that deleting a transaction actually removes it from the database
        """
        self.client.login(username='testuser', password='testpass123')
        
        # Delete the transaction
        response = self.client.post(
            reverse('delete_transaction', args=[self.expense_transaction.id])
        )
        
        # Check redirect to dashboard
        self.assertEqual(response.status_code, 302)
        
        # Verify the transaction was deleted
        self.assertFalse(
            Transaction.objects.filter(id=self.expense_transaction.id).exists()
        )
    
    def test_user_cannot_edit_other_users_transaction(self):
        """
        Test that users can only edit their own transactions
        """
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        
        # Login as the other user
        self.client.login(username='otheruser', password='otherpass123')
        
        # Try to edit the first user's transaction
        response = self.client.get(
            reverse('edit_transaction', args=[self.income_transaction.id])
        )
        
        # Should get 404 (not found)
        self.assertEqual(response.status_code, 404)
    
    def test_user_cannot_delete_other_users_transaction(self):
        """
        Test that users can only delete their own transactions
        """
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            password='otherpass123'
        )
        
        # Login as the other user
        self.client.login(username='otheruser', password='otherpass123')
        
        # Try to delete the first user's transaction
        response = self.client.post(
            reverse('delete_transaction', args=[self.income_transaction.id])
        )
        
        # Should get 404 (not found)
        self.assertEqual(response.status_code, 404)
        
        # Verify transaction still exists
        self.assertTrue(
            Transaction.objects.filter(id=self.income_transaction.id).exists()
        )
    
    def test_login_required_for_edit(self):
        """
        Test that login is required to edit transactions
        """
        # Don't login
        response = self.client.get(
            reverse('edit_transaction', args=[self.income_transaction.id])
        )
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
    
    def test_login_required_for_delete(self):
        """
        Test that login is required to delete transactions
        """
        # Don't login
        response = self.client.get(
            reverse('delete_transaction', args=[self.expense_transaction.id])
        )
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
