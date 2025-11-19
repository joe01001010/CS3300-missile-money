from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.contrib import messages
from .forms import TransactionForm
from .models import Transaction
from collections import defaultdict
from django.utils.timezone import localtime
from django.db.models import Q
from decimal import Decimal
from django.contrib.auth.models import User


class CustomLoginView(LoginView):
    """
    This class will handle the login functionality
    It will redirect to the login page after successful login
    There is no return value for this class
    """
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    
    def form_valid(self, form):
        """
        This function will handle valid login attempts
        It will return a 200 status code
        There is no return value for this function
        """
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)
    

    def form_invalid(self, form):
        """
        This function will handle invalid login attempts
        It will return a 400 status code
        There is no return value for this function
        """
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)


def register(request):
    """
    This function will register a new user
    It will redirect to the login page after successful registration
    There is no return value for this function
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    """
    This function will render the profile page
    It will return a 200 status code
    There is no return value for this function
    """
    return render(request, 'registration/profile.html')


def custom_logout(request):
    """
    This function will logout the user
    It will redirect to the home page
    There is no return value for this function
    """
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')


def submit_feedback(request):
    """
    This function will submit feedback to the support team
    It will send an email to the support team with the feedback
    There is no return value for this function
    This function is currently setup for testing, will need to change from_email and to when switching to production
    This function will redirect to the home page after successful submission
    """
    if request.method == "POST":
        user_email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        if not message:
            messages.error(request, "Please enter a message before submitting.")
            return redirect(request.META.get("HTTP_REFERER", "home"))

        subject = "Missile Money - User Feedback"
        body = f"Feedback message:\n\n{message}\n\nFrom: {user_email or 'Anonymous'}"

        email = EmailMessage(
            subject=subject,
            body=body,
            from_email="website@missile-money.com", # Change this for production usage. I made it this for local testing
            to=["support@missile-money.com"], # Change this for production usage. I made it this for local testing
            reply_to=[user_email] if user_email else None,
        )

        try:
            email.send(fail_silently=False)
            messages.success(request, "Thank you! Your feedback has been sent.")
        except Exception as e:
            messages.error(request, f"Failed to send feedback: {e}")

        return redirect(request.META.get("HTTP_REFERER", "home"))

    messages.error(request, "Invalid request method.")
    return redirect("home")


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()

            if transaction.type == 'expense' and form.cleaned_data['peer_payment']:
                recipient_user = form.cleaned_data['recipient']
                income_tx = Transaction.objects.create(
                    user=recipient_user,
                    type='income',
                    category='other_income',
                    amount=transaction.amount,
                    description=f"Peer payment from {request.user.username}",
                    peer_payment=True,
                )
                # link the transactions
                transaction.related_transaction = income_tx
                transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('dashboard')
    else:
        form = TransactionForm(user=request.user, initial={
            'type': request.GET.get('type','').lower()
        })
    return render(request, 'add_transaction.html', {'form': form})


@login_required
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    
    total_balance = 0
    for transaction in transactions:
        if transaction.type == 'income':
            total_balance += transaction.amount
        elif transaction.type == 'expense':
            total_balance -= transaction.amount
    
    monthly_income = sum(t.amount for t in transactions if t.type == 'income')
    monthly_expenses = sum(t.amount for t in transactions if t.type == 'expense')
    savings_goal = 0

    transactions_by_month = defaultdict(list)
    for t in transactions:
        month_key = t.date.strftime("%Y-%m")
        transactions_by_month[month_key].append(t)

    transactions_by_month = dict(sorted(transactions_by_month.items(), reverse=True))

    context = {
        'transactions': transactions,
        'transactions_by_month': transactions_by_month,
        'total_balance': total_balance,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'savings_goal': savings_goal,
    }
    return render(request, 'dashboard.html', context)


@login_required
def view_reports(request):
    """
    Render the reports page with optional filtering and search on the user's transactions.
    Users can filter by category, transaction type, date range, and a search term via GET params.
    """
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    # Extract query parameters for filtering
    category = request.GET.get('category')
    tx_type = request.GET.get('type')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search_query = request.GET.get('q')

    # Apply filters as needed
    if category:
        transactions = transactions.filter(category=category)
    if tx_type in ['income', 'expense']:
        transactions = transactions.filter(type=tx_type)
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    if search_query:
        transactions = transactions.filter(
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query)
        )

    # Calculate summary totals
    total_income = sum(t.amount for t in transactions if t.type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.type == 'expense')
    net_total = total_income - total_expenses

    # Combine category choices for dropdown
    categories = Transaction.INCOME_CATEGORIES + Transaction.EXPENSE_CATEGORIES

    context = {
        'transactions': transactions,
        'categories': categories,
        'selected_category': category,
        'selected_type': tx_type,
        'start_date': start_date,
        'end_date': end_date,
        'search_query': search_query,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_total': net_total,
    }
    return render(request, 'reports.html', context)


@login_required
def edit_transaction(request, transaction_id):
    """
    This function will edit an existing transaction
    It will redirect to the dashboard after successful edit
    There is no return value for this function
    """
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    
    if request.method == 'POST':
        transaction.type = request.POST.get('type')
        transaction.category = request.POST.get('category', '')
        transaction.amount = request.POST.get('amount')
        transaction.description = request.POST.get('description')
        transaction.save()
        messages.success(request, 'Transaction updated successfully!')
        return redirect('dashboard')
    
    return render(request, 'edit_transaction.html', {'transaction': transaction})


@login_required
def delete_transaction(request, transaction_id):
    """
    This function will delete a transaction
    It will redirect to the dashboard after successful deletion
    There is no return value for this function
    """
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('dashboard')
    
    return render(request, 'delete_transaction.html', {'transaction': transaction})


@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'reports.html', {'transactions': transactions})


@login_required
def send_payment(request):
    """
    This function takes a request as an argument
    Allow a logged‑in user to send money to another user
    Creates an expense for the sender and an income for the recipient in the 'peer' category
    Redirects back to the dashboard with a message on success or displays errors when invalid
    This function returns the send_payment.html template
    """
    if request.method == 'POST':
        recipient_username = request.POST.get('recipient', '').strip()
        amount_str = request.POST.get('amount', '').strip()
        description = request.POST.get('description', '').strip()

        errors = []
        try:
            recipient = User.objects.get(username=recipient_username)
            if recipient == request.user:
                errors.append("You cannot send money to yourself.")
        except User.DoesNotExist:
            errors.append("Recipient user does not exist.")

        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                errors.append("Amount must be positive.")
        except Exception:
            errors.append("Invalid amount.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('dashboard')

        Transaction.objects.create(
            user=request.user,
            type='expense',
            category='peer',
            amount=amount,
            description=description or f"Peer transfer to {recipient_username}"
        )
        Transaction.objects.create(
            user=recipient,
            type='income',
            category='peer',
            amount=amount,
            description=description or f"Peer transfer from {request.user.username}"
        )

        messages.success(request, f"Successfully sent ${amount} to {recipient_username}.")
        return redirect('dashboard')

    return render(request, 'send_payment.html')