from django.shortcuts import render, redirect
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
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('dashboard')
    else:
        form = TransactionForm()
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


def view_reports(request):
    return render(request, 'reports.html')