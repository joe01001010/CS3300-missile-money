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


class TransactionCategoryTestCase(TestCase):
    """
    Test cases for transaction categorization functionality
    """
    def setUp(self):
        """
        Set up test user before each test
        """
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Set up test client
        self.client = Client()
    

    def test_add_income_transaction_with_category(self):
        """
        Test that users can add an income transaction with a category
        """
        self.client.login(username='testuser', password='testpass123')
        
        # Add an income transaction with a category
        response = self.client.post(reverse('add_transaction'), {
            'type': 'income',
            'category': 'job',
            'amount': '3000.00',
            'description': 'Monthly Salary'
        })
        
        # Check redirect to dashboard
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/', response.url)
        
        # Verify the transaction was created with the category
        transaction = Transaction.objects.filter(user=self.user).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.type, 'income')
        self.assertEqual(transaction.category, 'job')
        self.assertEqual(transaction.amount, Decimal('3000.00'))
        self.assertEqual(transaction.description, 'Monthly Salary')
    

    def test_add_expense_transaction_with_category(self):
        """
        Test that users can add an expense transaction with a category
        """
        self.client.login(username='testuser', password='testpass123')
        
        # Add an expense transaction with a category
        response = self.client.post(reverse('add_transaction'), {
            'type': 'expense',
            'category': 'groceries',
            'amount': '150.50',
            'description': 'Weekly Groceries'
        })
        
        # Check redirect to dashboard
        self.assertEqual(response.status_code, 302)
        
        # Verify the transaction was created with the category
        transaction = Transaction.objects.filter(user=self.user).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.type, 'expense')
        self.assertEqual(transaction.category, 'groceries')
        self.assertEqual(transaction.amount, Decimal('150.50'))
        self.assertEqual(transaction.description, 'Weekly Groceries')
    

    def test_edit_transaction_updates_category(self):
        """
        Test that editing a transaction can update its category
        """
        self.client.login(username='testuser', password='testpass123')
        
        # Create a transaction
        transaction = Transaction.objects.create(
            user=self.user,
            type='income',
            category='job',
            amount=Decimal('2000.00'),
            description='Original Description'
        )
        
        # Edit the transaction to change category
        response = self.client.post(
            reverse('edit_transaction', args=[transaction.id]),
            {
                'type': 'income',
                'category': 'investments',
                'amount': '2000.00',
                'description': 'Investment Income'
            }
        )
        
        # Check redirect to dashboard
        self.assertEqual(response.status_code, 302)
        
        # Verify the category was updated
        updated_transaction = Transaction.objects.get(id=transaction.id)
        self.assertEqual(updated_transaction.category, 'investments')
        self.assertEqual(updated_transaction.description, 'Investment Income')
    

    def test_add_transaction_without_category(self):
        """
        Test that users can add a transaction without selecting a category
        """
        self.client.login(username='testuser', password='testpass123')
        
        # Add a transaction without a category
        response = self.client.post(reverse('add_transaction'), {
            'type': 'income',
            'category': '',
            'amount': '1000.00',
            'description': 'Cash Gift'
        })
        
        # Check redirect to dashboard
        self.assertEqual(response.status_code, 302)
        
        # Verify the transaction was created without a category
        transaction = Transaction.objects.filter(user=self.user).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.category, '')
    

    def test_category_display_method(self):
        """
        Test the get_category_display method returns correct display names
        """
        # Create income transaction with category
        income_transaction = Transaction.objects.create(
            user=self.user,
            type='income',
            category='reimbursements',
            amount=Decimal('500.00'),
            description='Travel Reimbursement'
        )
        
        # Verify display name
        self.assertEqual(income_transaction.get_category_display(), 'Reimbursements (non-taxable)')
        
        # Create expense transaction with category
        expense_transaction = Transaction.objects.create(
            user=self.user,
            type='expense',
            category='utilities_housing',
            amount=Decimal('800.00'),
            description='Monthly Rent'
        )
        
        # Verify display name
        self.assertEqual(expense_transaction.get_category_display(), 'Utilities/Housing')
        
        # Create transaction without category
        no_category = Transaction.objects.create(
            user=self.user,
            type='income',
            category='',
            amount=Decimal('100.00'),
            description='Misc Income'
        )
        
        # Verify display name for no category
        self.assertEqual(no_category.get_category_display(), 'Uncategorized')
    

    def test_all_income_categories_save_correctly(self):
        """
        Test that all income categories can be saved correctly
        """
        self.client.login(username='testuser', password='testpass123')
        
        income_categories = ['job', 'investments', 'reimbursements', 'other_income']
        
        for category in income_categories:
            response = self.client.post(reverse('add_transaction'), {
                'type': 'income',
                'category': category,
                'amount': '100.00',
                'description': f'Test {category}'
            })
            self.assertEqual(response.status_code, 302)
            
            transaction = Transaction.objects.filter(user=self.user, category=category).first()
            self.assertIsNotNone(transaction)
            self.assertEqual(transaction.category, category)
            self.assertEqual(transaction.type, 'income')
    
    
    def test_all_expense_categories_save_correctly(self):
        """
        Test that all expense categories can be saved correctly
        """
        self.client.login(username='testuser', password='testpass123')
        
        expense_categories = ['groceries', 'utilities_housing', 'recreation', 'other_expense']
        
        for category in expense_categories:
            response = self.client.post(reverse('add_transaction'), {
                'type': 'expense',
                'category': category,
                'amount': '50.00',
                'description': f'Test {category}'
            })
            self.assertEqual(response.status_code, 302)
            
            transaction = Transaction.objects.filter(user=self.user, category=category).first()
            self.assertIsNotNone(transaction)
            self.assertEqual(transaction.category, category)
            self.assertEqual(transaction.type, 'expense')


class ReportsViewTestCase(TestCase):
    """
    This class is designed to run test cases that will test the filtering logic for transactions from a users point of view
    This class is designed to be leveraged by the automated tests that django is doing and through github actions
    The report page should dipslay a list of the current users transactions
    The report page should allow filtering by transaction type, category, date range, and a free text search query 
    Teh report page should calculate total income, total expenses and the net total based on the filtered queryset
    """

    def setUp(self):
        """
        This function takes no arguments
        Set up a test user and a three transactions that can be filtered
        This function doesnt return anything
        """
        self.user = User.objects.create_user(
            username='joe_test_user',
            password='idklmao123123'
        )
        self.client = Client()

        Transaction.objects.create(
            user=self.user,
            type='income',
            category='job',
            amount=Decimal('1000.00'),
            description='Monthly salary'
        )
        Transaction.objects.create(
            user=self.user,
            type='expense',
            category='groceries',
            amount=Decimal('200.00'),
            description='Weekly groceries'
        )
        Transaction.objects.create(
            user=self.user,
            type='income',
            category='investments',
            amount=Decimal('500.00'),
            description='Stocks dividends'
        )

    def test_view_reports_displays_all_transactions_and_totals(self):
        """
        This fucntion takes no arguments
        Ensure the reports view lists all of the user's transactions when no filters are applied and computes the correct summary totals
        This function has no return value
        """
        self.client.login(username='joe_test_user', password='idklmao123123')

        response = self.client.get(reverse('view_reports'))
        self.assertEqual(response.status_code, 200)

        transactions = list(response.context['transactions'])
        self.assertEqual(len(transactions), 3)

        expected_income = sum(t.amount for t in transactions if t.type == 'income')
        expected_expenses = sum(t.amount for t in transactions if t.type == 'expense')
        expected_net = expected_income - expected_expenses

        self.assertEqual(response.context['total_income'], expected_income)
        self.assertEqual(response.context['total_expenses'], expected_expenses)
        self.assertEqual(response.context['net_total'], expected_net)

    def test_view_reports_filters_by_type(self):
        """
        This function takes no argumnets
        Verify that the reports view correctly filters transactions by the type query parameter
        This function returns nothing
        """
        self.client.login(username='joe_test_user', password='idklmao123123')

        response = self.client.get(reverse('view_reports'), {'type': 'income'})
        self.assertEqual(response.status_code, 200)

        transactions = list(response.context['transactions'])
        self.assertEqual(len(transactions), 2)
        for transaction in transactions:
            self.assertEqual(transaction.type, 'income')

        expected_income = sum(t.amount for t in transactions)
        expected_expenses = Decimal('0')
        expected_net = expected_income - expected_expenses

        self.assertEqual(response.context['total_income'], expected_income)
        self.assertEqual(response.context['total_expenses'], expected_expenses)
        self.assertEqual(response.context['net_total'], expected_net)


class PeerPaymentTestCase(TestCase):
    """
    This function takes a test case as an argument
    Test peer‑to‑peer payment functionality
    Ensure that valid payments create two transactions and invalid inputs do not
    This function doesnt return anything
    """
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='testpass')
        self.receiver = User.objects.create_user(username='receiver', password='testpass')
        self.client = Client()


    def test_send_payment_creates_transactions(self):
        self.client.login(username='sender', password='testpass')
        amount = Decimal('50.00')
        response = self.client.post(reverse('send_payment'), {
            'recipient': 'receiver',
            'amount': str(amount),
            'description': 'Test peer transfer'
        })
        # should redirect to dashboard on success
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard'), response.url)

        sender_tx = Transaction.objects.filter(user=self.sender, type='expense', category='peer').first()
        receiver_tx = Transaction.objects.filter(user=self.receiver, type='income', category='peer').first()
        self.assertIsNotNone(sender_tx)
        self.assertIsNotNone(receiver_tx)
        self.assertEqual(sender_tx.amount, amount)
        self.assertEqual(receiver_tx.amount, amount)


    def test_send_payment_invalid_recipient(self):
        self.client.login(username='sender', password='testpass')
        initial_count = Transaction.objects.count()
        response = self.client.post(reverse('send_payment'), {
            'recipient': 'nonexistent',
            'amount': '10.00',
            'description': 'Invalid recipient test'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard'), response.url)
        # No new transactions
        self.assertEqual(Transaction.objects.count(), initial_count)


    def test_send_payment_self_recipient(self):
        self.client.login(username='sender', password='testpass')
        initial_count = Transaction.objects.count()
        response = self.client.post(reverse('send_payment'), {
            'recipient': 'sender',
            'amount': '25.00',
            'description': 'Self payment test'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard'), response.url)
        self.assertEqual(Transaction.objects.count(), initial_count)