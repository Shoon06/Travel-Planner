
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
    
    user_type = forms.ChoiceField(
        choices=CustomUser.USER_TYPE_CHOICES,
        initial='user',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 
                  'user_type', 'first_name', 'last_name', 'phone_number', 
                  'location', 'bio', 'profile_picture', 'is_active')
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
        user.user_type = self.cleaned_data.get('user_type', 'user')
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.phone_number = self.cleaned_data.get('phone_number', '')
        user.location = self.cleaned_data.get('location', '')
        user.bio = self.cleaned_data.get('bio', '')
        user.is_active = self.cleaned_data.get('is_active', True)
        
        if commit:
            user.save()
            if self.cleaned_data.get('profile_picture'):
                user.profile_picture = self.cleaned_data['profile_picture']
                user.save()
        return user

# ... [rest of your existing forms] ...
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