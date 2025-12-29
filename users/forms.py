# C:\Users\ASUS\MyanmarTravelPlanner\users\forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Form for creating new users - allows duplicate usernames"""
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        """Ensure email is unique"""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def clean_username(self):
        """Allow duplicate usernames - no uniqueness check"""
        username = self.cleaned_data.get('username')
        return username  # No validation for duplicates


class CustomAuthenticationForm(AuthenticationForm):
    """Login form that uses email instead of username"""
    
    username = forms.EmailField(label="Email")
    
    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if email and password:
            try:
                user = CustomUser.objects.get(email=email)
                if user.check_password(password):
                    self.user_cache = user
                else:
                    raise forms.ValidationError("Invalid email or password.")
            except CustomUser.DoesNotExist:
                raise forms.ValidationError("Invalid email or password.")
        
        return self.cleaned_data