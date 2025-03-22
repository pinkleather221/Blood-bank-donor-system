from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import os

def send_donation_request_received(donor):
    """Send email when a donor requests to donate blood"""
    subject = 'Blood Donation Request Received'
    message = f"""
    Dear {donor.get_name},
    
    Your request to donate blood has been received. Please visit the Chuka Blood Bank for testing and donation.
    
    Thank you,
    Chuka Blood Bank
    """
    recipient = donor.email if donor.email else donor.user.email
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
        fail_silently=True,
    )

def send_donation_successful(donor, donation):
    """Send email when a donor's donation is successful"""
    subject = 'Blood Donation Successful'
    message = f"""
    Dear {donor.get_name},
    
    Congratulations! Your blood donation was successful. Thank you for your generosity. Your donation certificate is attached.
    
    Thank you,
    Chuka Blood Bank
    """
    recipient = donor.email if donor.email else donor.user.email
    
    # Update donor's last donation date
    donor.last_donation_date = timezone.now()
    donor.save()
    
    # Create an email with attachment
    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient]
    )
    
    # Generate certificate (placeholder - you'll need to implement actual certificate generation)
    # This is just a placeholder example
    # email.attach_file('/path/to/certificate.pdf')
    
    email.send(fail_silently=True)

def send_donation_failed(donor):
    """Send email when a donor fails health screening"""
    subject = 'Blood Donation Status'
    message = f"""
    Dear {donor.get_name},
    
    Unfortunately, you did not meet the donation requirements. Thank you for your willingness to help.
    
    Regards,
    Chuka Blood Bank
    """
    recipient = donor.email if donor.email else donor.user.email
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
        fail_silently=True,
    )

def send_donation_reminder(donor):
    """Send reminder email to donors after 3 months"""
    subject = 'Blood Donation Reminder'
    message = f"""
    Hello {donor.get_name},
    
    It's been 3 months since your last donation. We greatly appreciate your past contribution and would love to see you again at our blood bank!
    
    Best regards,
    Chuka Blood Bank
    """
    recipient = donor.email if donor.email else donor.user.email
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
        fail_silently=True,
    )

def send_patient_request_approved(patient, blood_request):
    """Send email when a patient's blood request is approved"""
    subject = 'Blood Request Approved'
    message = f"""
    Dear {patient.get_name},
    
    Your blood request for {blood_request.unit} units of {blood_request.bloodgroup} has been approved. Kindly visit the Chuka Blood Bank for collection.
    
    Regards,
    Chuka Blood Bank
    """
    recipient = patient.email if patient.email else patient.user.email
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
        fail_silently=True,
    )

def send_patient_request_unavailable(patient, blood_request):
    """Send email when requested blood type is unavailable"""
    subject = 'Blood Request Status'
    message = f"""
    Dear {patient.get_name},
    
    Unfortunately, the requested blood type {blood_request.bloodgroup} is currently unavailable. We will notify you if it becomes available.
    
    Regards,
    Chuka Blood Bank
    """
    recipient = patient.email if patient.email else patient.user.email
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
        fail_silently=True,
    )

def send_urgent_request_to_donors(blood_type, patient=None):
    """Send urgent alerts to matching blood type donors"""
    from donor.models import Donor  # Import here to avoid circular imports
    
    # Find all donors with matching blood type
    matching_donors = Donor.objects.filter(bloodgroup=blood_type)
    
    patient_info = ""
    if patient:
        patient_info = f" for patient {patient.get_name}"
    
    subject = f'URGENT: Blood Donation Request for Type {blood_type}'
    
    for donor in matching_donors:
        if donor.email or donor.user.email:
            message = f"""
            Dear {donor.get_name},
            
            Urgent Alert: A patient requires blood type {blood_type}. Kindly visit the Chuka Blood Bank if you are available to donate.
            
            Thank you,
            Chuka Blood Bank
            """
            recipient = donor.email if donor.email else donor.user.email
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
                fail_silently=True,
            )
    
    return len(matching_donors)
