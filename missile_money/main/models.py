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
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=20, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField(auto_now_add=True)

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

# --- Bill Splitting Models ---
class Bill(models.Model):
    title = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills_created')
    participants = models.ManyToManyField(User, through='BillShare', related_name='bills_participating')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - ${self.total_amount}"


class BillShare(models.Model):
    bill = models.ForeignKey('Bill', on_delete=models.CASCADE, related_name='shares')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_owed = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} owes ${self.amount_owed} for {self.bill.title}"
