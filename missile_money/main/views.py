# main/views.py
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from django.http import HttpResponseForbidden
from django.db.models import Sum

from .forms import TransactionForm
from .models import Transaction, Bill, BillShare
from django.utils import timezone


User = get_user_model()


# ---------------------------
# Authentication
# ---------------------------
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
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
    return render(request, 'registration/profile.html')


def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')


# ---------------------------
# Feedback
# ---------------------------
def submit_feedback(request):
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
            from_email="website@missile-money.com",
            to=["support@missile-money.com"],
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


# ---------------------------
# Transactions
# ---------------------------
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
        initial_type = request.GET.get('type', '').lower()
        form = TransactionForm(initial={'type': initial_type} if initial_type else {})
    return render(request, 'add_transaction.html', {'form': form})


@login_required
def edit_transaction(request, transaction_id):
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
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('dashboard')
    return render(request, 'delete_transaction.html', {'transaction': transaction})


# ---------------------------
# Dashboard (with bill split tracking)
# ---------------------------
@login_required
def dashboard(request):
    # --------- EXISTING: bill-splitting aware totals ---------
    gross = Transaction.objects.filter(user=request.user).aggregate(s=Sum('amount'))['s'] or Decimal('0.00')

    others_owe_all = BillShare.objects.filter(
        bill__created_by=request.user
    ).exclude(user=request.user).aggregate(s=Sum('amount_owed'))['s'] or Decimal('0.00')

    others_owe_paid = BillShare.objects.filter(
        bill__created_by=request.user, paid=True
    ).exclude(user=request.user).aggregate(s=Sum('amount_owed'))['s'] or Decimal('0.00')

    net_after_split = gross - others_owe_all
    net_cash_out    = gross - others_owe_paid

    # --------- NEW: compute your original dashboard cards ---------
    today = timezone.localdate()
    yr, mo = today.year, today.month

    qs = Transaction.objects.filter(user=request.user)

    # All-time totals for balance card
    total_income_all   = qs.filter(type='income').aggregate(s=Sum('amount'))['s'] or Decimal('0.00')
    total_expenses_all = qs.filter(type='expense').aggregate(s=Sum('amount'))['s'] or Decimal('0.00')
    total_balance      = total_income_all - total_expenses_all

    # This-month cards
    monthly_income = qs.filter(type='income',  date__year=yr, date__month=mo).aggregate(s=Sum('amount'))['s'] or Decimal('0.00')
    monthly_expenses = qs.filter(type='expense', date__year=yr, date__month=mo).aggregate(s=Sum('amount'))['s'] or Decimal('0.00')

    # Recent transactions list
    transactions = qs.order_by('-date')[:10]

    ctx = {
        # your original cards
        "total_balance": total_balance,
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "transactions": transactions,

        # bill-split summary numbers (even if you hide them in the template)
        "gross_expenses": gross,
        "others_owe_all": others_owe_all,
        "others_owe_paid": others_owe_paid,
        "net_after_split": net_after_split,
        "net_cash_out": net_cash_out,
    }
    return render(request, "dashboard.html", ctx)

# ---------------------------
# Reports
# ---------------------------
def view_reports(request):
    return render(request, 'reports.html')


# ---------------------------
# Bill Split
# ---------------------------
@login_required
def Bill_Split(request, transaction_id):
    tx = get_object_or_404(Transaction, id=transaction_id)

    if request.method == 'POST':
        total = Decimal(tx.amount).quantize(Decimal('0.01'))
        errors = []

        selected_ids = request.POST.getlist('participants')
        include_me = 'include_me' in request.POST

        participants = []
        amount_sum = Decimal('0.00')

        if include_me:
            amt_str = (request.POST.get('amount_me') or '').strip()
            try:
                amt = Decimal(amt_str).quantize(Decimal('0.01'))
            except (InvalidOperation, AttributeError):
                amt = None
            if amt is None or amt < 0:
                errors.append("Your amount must be a non-negative number.")
            else:
                participants.append((request.user, amt))
                amount_sum += amt

        qs = User.objects.filter(id__in=selected_ids)
        for u in qs:
            amt_str = (request.POST.get(f'amount_{u.id}') or '').strip()
            try:
                amt = Decimal(amt_str).quantize(Decimal('0.01'))
            except (InvalidOperation, AttributeError):
                amt = None
            if amt is None or amt < 0:
                errors.append(f"Amount for {u.username} must be a non-negative number.")
            else:
                participants.append((u, amt))
                amount_sum += amt

        diff = (total - amount_sum).quantize(Decimal('0.01'))

        if errors:
            return render(request, 'bill_split.html', {
                'transaction': tx,
                'users': User.objects.exclude(id=request.user.id),
                'error': " ".join(errors),
            })

        if abs(diff) > Decimal('0.01'):
            return render(request, 'bill_split.html', {
                'transaction': tx,
                'users': User.objects.exclude(id=request.user.id),
                'error': f"Entered amounts total ${amount_sum}, which differs from the transaction total ${total}.",
            })

        if diff != Decimal('0.00'):
            last_user, last_amt = participants[-1]
            participants[-1] = (last_user, (last_amt + diff).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

        bill = Bill.objects.create(
            title=f"Split of Transaction #{tx.id}",
            total_amount=tx.amount,
            created_by=request.user,
        )
        for u, amt in participants:
            BillShare.objects.create(bill=bill, user=u, amount_owed=amt)

        messages.success(request, "Bill created and split successfully.")
        return redirect('bill_detail', bill_id=bill.id)

    users = User.objects.exclude(id=request.user.id)
    return render(request, 'bill_split.html', {'transaction': tx, 'users': users})


# ---------------------------
# View Bills + Details
# ---------------------------
@login_required
def view_bills(request):
    bills = Bill.objects.filter(created_by=request.user).order_by('-date_created')
    return render(request, 'view_bills.html', {'bills': bills})


@login_required
def bill_detail(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id, created_by=request.user)
    shares = BillShare.objects.filter(bill=bill).select_related('user').order_by('id')

    total_others = Decimal('0.00')
    total_paid = Decimal('0.00')
    for s in shares:
        if s.user_id != bill.created_by_id:
            total_others += s.amount_owed
            if s.paid:
                total_paid += s.amount_owed
    total_unpaid = total_others - total_paid

    ctx = {
        'bill': bill,
        'shares': shares,
        'total_others': f"{total_others:.2f}",
        'total_paid': f"{total_paid:.2f}",
        'total_unpaid': f"{total_unpaid:.2f}",
    }
    return render(request, 'bill_detail.html', ctx)


# ---------------------------
# Toggle Paid / Unpaid
# ---------------------------
@login_required
def toggle_share_paid(request, bill_id, share_id):
    bill = get_object_or_404(Bill, id=bill_id)
    share = get_object_or_404(BillShare, id=share_id, bill=bill)
    if bill.created_by_id != request.user.id:
        return HttpResponseForbidden("You can't modify this bill.")
    share.paid = not share.paid
    share.save(update_fields=["paid"])
    messages.success(request, f"Marked {share.user.username} as {'paid' if share.paid else 'unpaid'}.")
    return redirect('bill_detail', bill_id=bill.id)
