from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import os
import re
import logging
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.timezone import make_aware
logger = logging.getLogger(__name__)

def validate_email_address(email):
    """Validate email format and check domain"""
    try:
        validate_email(email)
        logger.debug(f"Email validation successful for: {email}")
        return True
    except ValidationError as e:
        logger.warning(f"Invalid email format for {email}: {str(e)}")
        return False

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
    
    logger.info(f"Preparing donation request email to {recipient}")
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
        logger.info(f"Successfully sent donation request email to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send donation request email to {recipient}: {str(e)}")
        raise

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
    
    logger.info(f"Preparing donation success email to {recipient}")
    
    # Update donor's last donation date
    donor.last_donation_date = timezone.now().date() - timedelta(days=90)
    donor.save()
    logger.debug(f"Updated last donation date for donor {donor.id}")
    
    try:
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
        
        email.send(fail_silently=False)
        logger.info(f"Successfully sent donation success email to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send donation success email to {recipient}: {str(e)}")
        raise

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
    
    logger.info(f"Preparing donation failed email to {recipient}")
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
        logger.info(f"Successfully sent donation failed email to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send donation failed email to {recipient}: {str(e)}")
        raise

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
    
    logger.info(f"Preparing donation reminder email to {recipient}")
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
        logger.info(f"Successfully sent donation reminder email to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send donation reminder email to {recipient}: {str(e)}")
        raise

def send_patient_request_approved(patient, blood_request):
    """Send email when a patient's blood request is approved"""
    subject = 'Blood Request Approved'
    message = f"""
    Dear {patient.get_name()},
    
    Your blood request for {blood_request.unit} units of {blood_request.bloodgroup} has been approved. Kindly visit the Chuka Blood Bank for collection.
    
    Regards,
    Chuka Blood Bank
    """
    recipient = patient.email if patient.email else patient.user.email
    
    logger.info(f"Preparing request approved email to {recipient}")
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
        logger.info(f"Successfully sent request approved email to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send request approved email to {recipient}: {str(e)}")
        raise

def send_patient_request_unavailable(patient, blood_request):
    """Send email when requested blood type is unavailable"""
    subject = 'Blood Request Status'
    message = f"""
    Dear {patient.get_name()},
    
    Unfortunately, the requested blood type {blood_request.bloodgroup} is currently unavailable. We will notify you if it becomes available.
    
    Regards,
    Chuka Blood Bank
    """
    recipient = patient.email if patient.email else patient.user.email
    
    logger.info(f"Preparing request unavailable email to {recipient}")
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
        logger.info(f"Successfully sent request unavailable email to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send request unavailable email to {recipient}: {str(e)}")
        raise

def send_urgent_request_to_donors(blood_type, patient=None):
    """Send urgent alerts to matching blood type donors"""
    from donor.models import Donor  # Import here to avoid circular imports
    
    # Find all donors with matching blood type
    matching_donors = Donor.objects.filter(bloodgroup=blood_type)
    logger.info(f"Found {len(matching_donors)} donors with blood type {blood_type}")
    
    patient_info = ""
    if patient:
        patient_info = f" for patient {patient.get_name()}"
    
    subject = f'URGENT: Blood Donation Request for Type {blood_type}'
    success_count = 0
    
    for donor in matching_donors:
        if donor.email or donor.user.email:
            message = f"""
            Dear {donor.get_name},
            
            Urgent Alert: A patient requires blood type {blood_type}. Kindly visit the Chuka Blood Bank if you are available to donate.
            
            Thank you,
            Chuka Blood Bank
            """
            recipient = donor.email if donor.email else donor.user.email
            
            logger.info(f"Preparing urgent request email to {recipient}")
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient],
                    fail_silently=False,
                )
                success_count += 1
                logger.info(f"Successfully sent urgent request email to {recipient}")
            except Exception as e:
                logger.error(f"Failed to send urgent request email to {recipient}: {str(e)}")
    
    logger.info(f"Sent {success_count} urgent request emails out of {len(matching_donors)}")
    return success_count
