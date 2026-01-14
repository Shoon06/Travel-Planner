# C:\Users\ASUS\MyanmarTravelPlanner\planner\templatetags\custom_filters.py
from django import template

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