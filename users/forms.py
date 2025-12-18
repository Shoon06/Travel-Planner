from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'your.email@example.com'
        }),
        help_text="Required. Enter a valid email address."
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter your username'
            }),
        }
    
    def clean_email(self):
        """Email must be unique"""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(
                "This email is already registered. Please use a different email or login."
            )
        return email
    
    def clean_username(self):
        """Username doesn't need to be unique, but we'll keep basic validation"""
        username = self.cleaned_data.get('username')
        return username
    
    def clean(self):
        """Check for exact duplicates (same username AND same email)"""
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        
        if username and email:
            # Check if the exact combination exists
            if CustomUser.objects.filter(username=username, email=email).exists():
                raise ValidationError(
                    "A user with this username and email already exists."
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.user_type = 'user'
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Email or Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'your.email@example.com or username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg', 
            'placeholder': 'Enter your password'
        })
    )
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            # Since multiple users can have the same username,
            # we need to authenticate by email if provided
            
            if '@' in username:
                # It's an email, try to authenticate with email
                try:
                    # Since email is unique, get the user
                    user = CustomUser.objects.get(email=username)
                    # Now authenticate with the actual username
                    self.user_cache = authenticate(
                        self.request,
                        username=user.username,
                        password=password
                    )
                except CustomUser.DoesNotExist:
                    self.user_cache = None
            else:
                # It's a username, but there might be multiple users with same username
                # We need to find the right one
                users = CustomUser.objects.filter(username=username)
                
                if users.exists():
                    # Try each user until we find one that authenticates
                    for user in users:
                        auth_user = authenticate(
                            self.request,
                            username=user.username,
                            password=password
                        )
                        if auth_user:
                            self.user_cache = auth_user
                            break
                    else:
                        self.user_cache = None
                else:
                    self.user_cache = None
            
            if self.user_cache is None:
                raise ValidationError(
                    "Please enter a correct email/username and password. "
                    "Note that both fields may be case-sensitive."
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data