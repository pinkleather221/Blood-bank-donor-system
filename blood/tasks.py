# tasks.py in your blood app

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from datetime import timedelta
from django.utils import timezone

from blood.models import User
from donor.models import Donor

def send_eligible_donor_reminders():
    """Task to send reminders to donors who are eligible to donate again"""
    three_months_ago = timezone.now().date() - timedelta(days=90)

    eligible_donors = Donor.objects.filter(
        status='APPROVED',
        last_donation_date__lt=three_months_ago,
        email__isnull=False
    )
    
    for donor in eligible_donors:
        # Only send if they haven't been reminded in the last 30 days
        if not hasattr(donor, 'last_reminder_date') or donor.last_reminder_date < (datetime.now().date() - timedelta(days=30)):
            context = {
                'name': donor.user.first_name or donor.user.username,
                'donation_date': donor.last_donation_date.strftime('%B %d, %Y') if donor.last_donation_date else 'your previous donation',
                'blood_group': donor.bloodgroup,
                'hospital_name': 'Chuka Blood Bank',  # Replace with your actual name
                'contact_number': '123-456-7890'  # Replace with your actual number
            }
            
            message = f"""Dear {context['name']},

            We hope this email finds you well. According to our records, you are now eligible to donate blood again since your last donation date of {context['donation_date']}.

            Your blood type {context['blood_group']} is currently needed in our blood bank. Would you like to schedule your next donation?

            Thank you for your continued support in saving lives.

            Warm regards,
            {context['hospital_name']} Blood Bank Team
            {context['contact_number']}"""
            
            subject = "You're Eligible to Donate Blood Again"
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [donor.email],
                    fail_silently=False,
                )
                # Update last reminder date
                donor.last_reminder_date = timezone.now().date()

                donor.save()
            except Exception as e:
                print(f"Failed to send reminder to {donor.email}: {str(e)}")
