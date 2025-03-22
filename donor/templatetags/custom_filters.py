from django import template
from datetime import timedelta

register = template.Library()

@register.filter
def date_add(value, days):
    try:
        return value + timedelta(days=int(days))
    except (ValueError, TypeError):
        return value
