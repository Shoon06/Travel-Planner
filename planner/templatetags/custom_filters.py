from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def multiply_and_format(value, arg):
    """Multiply and format as MMK with commas"""
    try:
        result = float(value) * float(arg)
        return f"{intcomma(int(result))} MMK"
    except (ValueError, TypeError):
        return "0 MMK"

@register.filter
def format_mmk(value):
    """Format number as Myanmar Kyats (MMK)"""
    try:
        value = float(value)
        return f"{intcomma(int(value))} MMK"
    except (ValueError, TypeError):
        return "0 MMK"

@register.filter
def intcomma_mmk(value):
    """Add commas to numbers for MMK display"""
    return intcomma(value)

@register.filter
def calculate_total_cost(trip):
    """Calculate total cost for a trip"""
    try:
        return trip.get_total_cost_in_mmk()
    except:
        return 0

@register.filter
def get_cost_breakdown(trip):
    """Get cost breakdown for a trip"""
    try:
        return trip.get_cost_breakdown()
    except:
        return {}