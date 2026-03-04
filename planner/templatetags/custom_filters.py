# C:\Users\ASUS\MyanmarTravelPlanner\planner\templatetags\custom_filters.py
from django import template
import urllib.parse
from decimal import Decimal

register = template.Library()

@register.filter
def divide(value, arg):
    """Divide the value by the argument"""
    try:
        if arg == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def subtract(value, arg):
    """Subtract the argument from the value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add(value, arg):
    """Add the argument to the value"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def mmk_currency(value):
    """Format value as MMK currency"""
    try:
        value = float(value)
        return f"{value:,.0f} MMK"
    except (ValueError, TypeError):
        return "0 MMK"

@register.filter
def days_since(date):
    """Calculate days since a date"""
    from django.utils import timezone
    if not date:
        return 0
    delta = timezone.now().date() - date
    return delta.days

# NEW FILTERS ADDED BELOW

@register.filter
def replace(value, arg):
    """Replace characters in string. Usage: {{ value|replace:"old,new" }}"""
    if not value or not arg:
        return value
    try:
        old, new = arg.split(',', 1)
        return str(value).replace(old.strip(), new.strip())
    except:
        return value

@register.filter
def urlencode(value):
    """URL encode a string"""
    try:
        return urllib.parse.quote(str(value))
    except:
        return value

@register.filter
def contains(list_obj, item):
    """Check if item is in list"""
    if not list_obj:
        return False
    try:
        return item in list_obj
    except:
        return False

@register.filter
def format_amenity(amenity):
    """Format amenity name for display"""
    if not amenity:
        return ""
    # Replace underscores with spaces and capitalize
    return str(amenity).replace('_', ' ').title()

@register.filter
def first_n_items(list_obj, n):
    """Get first n items from list"""
    if not list_obj:
        return []
    try:
        return list_obj[:int(n)]
    except:
        return list_obj

@register.filter
def list_length(list_obj):
    """Get length of list"""
    if not list_obj:
        return 0
    try:
        return len(list_obj)
    except:
        return 0