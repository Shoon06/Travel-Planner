from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    
    # Override the username field to remove unique constraint
    username = models.CharField(
        max_length=150,
        unique=False,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    
    # Make email field unique instead
    email = models.EmailField(unique=True)
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='user')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # Social features
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    def is_admin_user(self):
        """Check if user has admin privileges"""
        return self.user_type == 'admin' or self.is_staff or self.is_superuser
    
    def is_regular_user(self):
        return self.user_type == 'user'
    
    # Add property for template access
    @property
    def is_admin(self):
        return self.is_admin_user()
    
    # Save method to ensure admin users have correct permissions
    def save(self, *args, **kwargs):
        if self.user_type == 'admin' and not self.is_staff:
            self.is_staff = True
        elif self.user_type == 'user' and self.is_staff:
            self.is_staff = False
        super().save(*args, **kwargs)