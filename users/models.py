# C:\Users\ASUS\MyanmarTravelPlanner\users\models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """Custom manager for CustomUser with email as username field"""
    
    def create_user(self, email, username, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    
    # Override username field to be NON-UNIQUE (allows duplicates)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=False,  # CHANGED: This allows duplicate usernames
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
    )
    
    # Override email field to be UNIQUE (no duplicates)
    email = models.EmailField(
        _('email address'),
        unique=True,  # CHANGED: Email must be unique
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    
    # Use email for authentication/login instead of username
    USERNAME_FIELD = 'email'  # Login with email
    REQUIRED_FIELDS = ['username']  # Username is still required but not for login
    
    # Use custom manager
    objects = CustomUserManager()
    
    # Your custom fields
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='user')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # Social features
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        # Add ordering to handle duplicate usernames
        ordering = ['email', 'username']
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    def is_admin_user(self):
        """Check if user has admin privileges"""
        return self.user_type == 'admin' or self.is_staff or self.is_superuser
    
    def is_regular_user(self):
        return self.user_type == 'user'
    
    @property
    def is_admin(self):
        return self.is_admin_user()
    
    def save(self, *args, **kwargs):
        # Normalize email to lowercase
        if self.email:
            self.email = self.email.lower()
        
        # Ensure username is not empty
        if not self.username:
            # Use part of email as username if empty
            self.username = self.email.split('@')[0]
        
        # Ensure admin users have correct permissions
        if self.user_type == 'admin' and not self.is_staff:
            self.is_staff = True
        elif self.user_type == 'user' and self.is_staff:
            self.is_staff = False
        
        super().save(*args, **kwargs)
class SystemSettings(models.Model):
    """System-wide settings stored in database"""
    site_name = models.CharField(max_length=100, default="GoMyanmar")
    site_description = models.TextField(default="Myanmar's Premier Travel Planning Platform")
    default_currency = models.CharField(max_length=10, default="MMK - Myanmar Kyat")
    maintenance_mode = models.BooleanField(default=False)
    
    # Email settings
    smtp_host = models.CharField(max_length=100, default="smtp.gmail.com")
    smtp_port = models.IntegerField(default=587)
    email_address = models.EmailField(default="noreply@gomyanmar.com")
    email_password = models.CharField(max_length=255, blank=True)
    enable_email_notifications = models.BooleanField(default=False)
    
    # System info (auto-updated)
    last_backup = models.DateTimeField(null=True, blank=True)
    last_maintenance = models.DateTimeField(null=True, blank=True)
    version = models.CharField(max_length=20, default="1.0.0")
    
    class Meta:
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def __str__(self):
        return "System Settings"