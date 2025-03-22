
from django import template
from datetime import timedelta, datetime
from django.utils import timezone

register = template.Library()

@register.filter(name='date_add')
def date_add(value, arg):
    """
    Add a specific time period to a date
    Usage: {{ value|date_add:"days=3" }} or {{ value|date_add:"months=3" }}
    """
    if value is None:
        return value
    
    parts = arg.split('=')
    if len(parts) != 2:
        return value
    
    unit = parts[0]
    amount = int(parts[1])
    
    if unit == 'days':
        return value + timedelta(days=amount)
    elif unit == 'months':
        # Calculate months by adding days (approximate)
        new_month = value.month + amount
        new_year = value.year + (new_month - 1) // 12
        new_month = ((new_month - 1) % 12) + 1
        
        try:
            return value.replace(year=new_year, month=new_month)
        except ValueError:
            # Handle cases when the day is invalid for the target month (e.g., February 30)
            last_day = [31, 29 if new_year % 4 == 0 and (new_year % 100 != 0 or new_year % 400 == 0) else 28, 
                        31, 30, 31, 30, 31, 31, 30, 31, 30, 31][new_month - 1]
            return value.replace(year=new_year, month=new_month, day=min(value.day, last_day))
    
    return value

@register.filter(name='subtract')
def subtract(value, arg):
    """Subtract the arg from the value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value