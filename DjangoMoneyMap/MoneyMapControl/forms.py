from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Transaction, Budget, Goal

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(max_length=150, required=True, label='Username')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=150, required=True, label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('username', 'password')

class ForgotPasswordForm(forms.Form):
    username = forms.CharField(max_length=150, label="Username")
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
        
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'category', 'amount', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'limit']
        widgets = {
            'category': forms.TextInput(attrs={
                'class': 'border-gray-300 rounded-md p-2 w-full',
                'placeholder': 'Category name'
            }),
            'limit': forms.NumberInput(attrs={
                'class': 'border-gray-300 rounded-md p-2 w-full',
                'placeholder': 'Limit (₹)'
            }),
        }
        
class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ['name', 'target_amount', 'saved_amount']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border-gray-300 rounded-md p-2 w-full', 'placeholder': 'Goal name'}),
            'target_amount': forms.NumberInput(attrs={'class': 'border-gray-300 rounded-md p-2 w-full', 'placeholder': 'Target (₹)'}),
            'saved_amount': forms.NumberInput(attrs={'class': 'border-gray-300 rounded-md p-2 w-full', 'placeholder': 'Saved (₹)'}),
        }
