from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import os
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def send_donation_request_confirmation(donor):
    """Send confirmation email when donor requests to donate blood"""
    subject = 'Blood Donation Request Received'
    message = f"Hello {donor.get_name},\n\nYour request to donate blood has been received. Please visit the Chuka Blood Bank for testing and donation.\n\nThank you for your generosity.\n\nChuka Blood Bank"
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [donor.get_email],
        fail_silently=False,
    )

def generate_donation_certificate(donor, donation):
    """Generate a PDF donation certificate"""
    template = get_template('donor/donation_certificate.html')
    context = {
        'donor_name': donor.get_name,
        'blood_group': donation.bloodgroup,
        'units': donation.unit,
        'date': donation.date,
    }
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None

def send_donation_success_email(donor, donation):
    """Send email when donor passes health screening"""
    subject = 'Blood Donation Successful'
    message = f"Hello {donor.get_name},\n\nCongratulations! Your blood donation was successful. Thank you for your generosity.\n\nChuka Blood Bank"
    
    # Generate PDF certificate
    pdf = generate_donation_certificate(donor, donation)
    
    email = EmailMessage(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [donor.get_email]
    )
    
    if pdf:
        email.attach('donation_certificate.pdf', pdf, 'application/pdf')
    
    email.send(fail_silently=False)
    
    # Update the donor's last donation date
    donor.last_donation_date = donation.date
    donor.save()

def send_donation_failure_email(donor):
    """Send email when donor fails health screening"""
    subject = 'Blood Donation Status'
    message = f"Hello {donor.get_name},\n\nUnfortunately, you did not meet the donation requirements. Thank you for your willingness to help.\n\nChuka Blood Bank"
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [donor.get_email],
        fail_silently=False,
    )

def send_donation_reminder(donor):
    """Send reminder email after 3 months from last donation"""
    subject = 'Blood Donation Reminder'
    message = f"Hello {donor.get_name},\n\nIt's been 3 months since your last donation. We greatly appreciate your past contribution and would love to see you again at our blood bank!\n\nChuka Blood Bank"
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [donor.get_email],
        fail_silently=False,
    )

def send_blood_request_approved(patient, request):
    """Send email when patient's blood request is approved"""
    subject = 'Blood Request Approved'
    message = f"Hello {patient.get_name},\n\nYour blood request has been approved. Kindly visit the Chuka Blood Bank for collection.\n\nChuka Blood Bank"
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [patient.get_email],
        fail_silently=False,
    )

def send_blood_request_denied(patient, request):
    """Send email when patient's blood request is denied due to unavailability"""
    subject = 'Blood Request Status'
    message = f"Hello {patient.get_name},\n\nUnfortunately, the requested blood type {request.bloodgroup} is currently unavailable. We will notify you if it becomes available.\n\nChuka Blood Bank"
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [patient.get_email],
        fail_silently=False,
    )

def send_urgent_donation_request(donor, blood_type):
    """Send urgent alert to matching donors"""
    subject = 'URGENT: Blood Donation Request'
    message = f"Hello {donor.get_name},\n\nUrgent Alert: A patient requires blood type {blood_type}. Kindly visit the Chuka Blood Bank if you are available to donate.\n\nYour prompt response could save a life.\n\nChuka Blood Bank"
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [donor.get_email],
        fail_silently=False,
    )