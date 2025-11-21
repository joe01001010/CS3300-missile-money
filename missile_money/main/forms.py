from django import forms
from .models import Transaction, SavingsGoal
from django.contrib.auth.models import User

class TransactionForm(forms.ModelForm):
    peer_payment = forms.BooleanField(required=False)
    recipient = forms.ModelChoiceField(
        queryset=User.objects.none(), required=False,
        widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Transaction
        fields = ['type', 'category', 'amount', 'description', 'peer_payment', 'recipient']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control', 'onchange': 'updateCategories()'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['recipient'].queryset = User.objects.exclude(id=user.id)
        else:
            self.fields['recipient'].queryset = User.objects.all()
        # Set initial category choices based on transaction type
        if self.instance and self.instance.pk:
            # Editing existing transaction
            if self.instance.type == 'income':
                self.fields['category'].choices = Transaction.INCOME_CATEGORIES
            elif self.instance.type == 'expense':
                self.fields['category'].choices = Transaction.EXPENSE_CATEGORIES
        elif 'type' in self.data:
            # Form was submitted with a type
            transaction_type = self.data.get('type')
            if transaction_type == 'income':
                self.fields['category'].choices = Transaction.INCOME_CATEGORIES
            elif transaction_type == 'expense':
                self.fields['category'].choices = Transaction.EXPENSE_CATEGORIES
        else:
            # Default to empty choices
            self.fields['category'].choices = []


class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['name', 'target_amount', 'target_date']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name your goal', 'class': 'form-input'}),
            'target_amount': forms.NumberInput(attrs={'placeholder': 'Amount to save', 'class': 'form-input', 'step': '0.01'}),
            'target_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }