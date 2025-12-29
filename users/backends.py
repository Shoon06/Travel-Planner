# C:\Users\ASUS\MyanmarTravelPlanner\users\backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Custom authentication backend that allows login with either email or username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        
        username = username.strip().lower()
        
        try:
            # Try by email first (email is unique)
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            try:
                # Try by username (case-insensitive)
                user = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                # User not found
                return None
            except User.MultipleObjectsReturned:
                # If multiple users have same username, get first active one
                user = User.objects.filter(username__iexact=username, is_active=True).first()
        except User.MultipleObjectsReturned:
            # This shouldn't happen since email is unique, but just in case
            user = User.objects.filter(email=username, is_active=True).first()
        
        # Check password
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None