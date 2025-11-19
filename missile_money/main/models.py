from django.db import models
from django.contrib.auth.models import User

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