from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    category = forms.ChoiceField(choices=[], required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Transaction
        fields = ['type', 'category', 'amount', 'description']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control', 'onchange': 'updateCategories()'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
