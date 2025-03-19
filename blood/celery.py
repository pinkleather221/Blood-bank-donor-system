import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodbank.settings')

app = Celery('bloodbank')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Create a new file: bloodbank/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from donor.models import Donor
from .utils.email_service import send_donation_reminder

@shared_task
def send_donation_reminders():
    """
    Send reminders to donors who donated 3 months ago
    """
    three_months_ago = timezone.now().date() - timedelta(days=90)
    
    # Find donors who donated approximately 3 months ago
    eligible_donors = Donor.objects.filter(
        last_donation_date__gte=three_months_ago - timedelta(days=3),
        last_donation_date__lte=three_months_ago + timedelta(days=3)
    )
    
    for donor in eligible_donors:
        send_donation_reminder(donor)
        
    return f"Sent reminders to {eligible_donors.count()} donors"

# In bloodbank/settings.py add:
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'send-donation-reminders': {
        'task': 'bloodbank.tasks.send_donation_reminders',
        'schedule': crontab(hour=9, minute=0),  # Run daily at 9 AM
    },
}