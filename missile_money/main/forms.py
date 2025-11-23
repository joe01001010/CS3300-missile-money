from django import forms
from .models import Transaction, SavingsGoal, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class EditProfilePictureForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture']


class CustomUserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)
    email = forms.EmailField(required=True)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            'profile_picture',
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

            profile_picture = self.cleaned_data.get('profile_picture')
            UserProfile.objects.create(
                user=user,
                profile_picture=profile_picture
            )
        return user


class TransactionForm(forms.ModelForm):
    """
    This form will handle creating and editing the transactions
    This form is used for standards entries and peer to peer payments
    This has features so users cant select themselves as a recipiend
    Will update categories based on expense or income
    """
    peer_payment = forms.BooleanField(required=False)
    recipient = forms.ModelChoiceField(
        queryset=User.objects.none(), required=False,
        widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        """
        This defines the fields configuration widgets and the default styles for all the inputs
        """
        model = Transaction
        fields = ['type', 'category', 'amount', 'description', 'peer_payment', 'recipient']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control', 'onchange': 'updateCategories()'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        """
        This function is used to initialize variables
        This will override the none with the currently logged in user
        This function will set the initial category choices based on transaction type
        This function has logic for if editing the existing transaction
        This function will have logic if the form is being submitted with a type
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['recipient'].queryset = User.objects.exclude(id=user.id)
        else:
            self.fields['recipient'].queryset = User.objects.all()
        if self.instance and self.instance.pk:
            if self.instance.type == 'income':
                self.fields['category'].choices = Transaction.INCOME_CATEGORIES
            elif self.instance.type == 'expense':
                self.fields['category'].choices = Transaction.EXPENSE_CATEGORIES
        elif 'type' in self.data:
            transaction_type = self.data.get('type')
            if transaction_type == 'income':
                self.fields['category'].choices = Transaction.INCOME_CATEGORIES
            elif transaction_type == 'expense':
                self.fields['category'].choices = Transaction.EXPENSE_CATEGORIES
        else:
            self.fields['category'].choices = []


class SavingsGoalForm(forms.ModelForm):
    """
    This form allows the user to define goal name target amount and date to achieve it by
    """
    class Meta:
        model = SavingsGoal
        fields = ['name', 'target_amount', 'target_date']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name your goal', 'class': 'form-input'}),
            'target_amount': forms.NumberInput(attrs={'placeholder': 'Amount to save', 'class': 'form-input', 'step': '0.01'}),
            'target_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }