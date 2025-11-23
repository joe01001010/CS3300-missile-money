from django.db import models
from django.contrib.auth.models import User


"""
These models are what will have fields in the django database
All properties and values associated with a user should have a cascading effect
If a user deletes their account all their stuff is deleted as well
"""


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    INCOME_CATEGORIES = [
        ('job', 'Job'),
        ('investments', 'Investments'),
        ('reimbursements', 'Reimbursements (non-taxable)'),
        ('other_income', 'Other'),
    ]

    EXPENSE_CATEGORIES = [
        ('groceries', 'Groceries'),
        ('utilities_housing', 'Utilities/Housing'),
        ('recreation', 'Recreation'),
        ('other_expense', 'Other'),
        ('peer', 'Peer Transfer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=20, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField(auto_now_add=True)

    peer_payment = models.BooleanField(default=False)
    recipient = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='received_payments')
    related_transaction = models.OneToOneField( 'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='peer_counterpart')

    def __str__(self):
        if self.peer_payment and self.recipient:
            return f"{self.user.username} paid {self.recipient.username} {self.amount}"
        return super().__str__()

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.amount}"
    
    def get_category_display(self):
        """Returns the display name for the category based on transaction type"""
        if self.type == 'income':
            for value, label in self.INCOME_CATEGORIES:
                if value == self.category:
                    return label
        elif self.type == 'expense':
            for value, label in self.EXPENSE_CATEGORIES:
                if value == self.category:
                    return label
        return self.category or 'Uncategorized'


class SavingsGoal(models.Model):
    """
    This class is for the users to set a savings goal
    This will dynamicalls create variables for the progress percentage
    current amount saved
    a display of the goal itself
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="My Savings Goal")
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    target_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def current_amount(self):
        return Transaction.objects.filter(user=self.user, type='income', category='savings').aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    @property
    def progress_percentage(self):
        if self.target_amount > 0:
            return min(100, (self.current_amount / self.target_amount) * 100)
        return 0

    def __str__(self):
        return f"{self.user.username} - {self.name} (${self.target_amount}) by {self.target_date}"