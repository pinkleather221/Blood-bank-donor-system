from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from donor.models import Donor
from blood.email_utils import send_donation_reminder

@shared_task
def send_three_month_donation_reminders():
    """Task to send reminders to donors who donated 3 months ago"""
    # Calculate the date 3 months ago
    three_months_ago = timezone.now() - timedelta(days=90)
    # Get all donors who donated around that time (within a day tolerance)
    eligible_donors = Donor.objects.filter(
        last_donation_date__date__gte=three_months_ago.date() - timedelta(days=1),
        last_donation_date__date__lte=three_months_ago.date() + timedelta(days=1)
    )
    
    reminder_count = 0
    for donor in eligible_donors:
        send_donation_reminder(donor)
        reminder_count += 1
    
    return f"Sent {reminder_count} donation reminders."