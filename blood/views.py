from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date
from django.core.mail import send_mail
from django.contrib.auth.models import User
from donor import models as dmodels
from patient import models as pmodels
from donor import forms as dforms
from patient import forms as pforms
from blood.models import BloodRequest, EmailCampaign
from django.contrib import messages
from django.template.loader import render_to_string
from donor.models import Donor
from patient.models import  Patient
from datetime import datetime, timedelta
from django.utils.safestring import mark_safe
from django.core.serializers.json import DjangoJSONEncoder
# mod 4
import requests
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
#mod new
import logging 
from django.core.mail import EmailMessage, get_connection
#end of mod new
# Configure logging for email sending
logger = logging.getLogger(__name__)

# mod 2 chatbot 
def chat_page(request):
    return render(request, 'blood/chat_widget.html')

#mod 5

RASA_API_URL = "http://localhost:5005/webhooks/rest/webhook"  # Adjust port if needed

@csrf_exempt
def chat_endpoint(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            
            # Send message to Rasa
            rasa_response = requests.post(
                RASA_API_URL,
                json={"sender": "user", "message": message}
            )
            
            # Process Rasa response
            responses = rasa_response.json()
            messages = [resp.get('text', '') for resp in responses]
            
            return JsonResponse({
                'status': 'success',
                'messages': messages
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

# ### mod 5 end 



def home_view(request):
    x=models.Stock.objects.all()
    print(x)
    if len(x)==0:
        blood1=models.Stock()
        blood1.bloodgroup="A+"
        blood1.save()

        blood2=models.Stock()
        blood2.bloodgroup="A-"
        blood2.save()

        blood3=models.Stock()
        blood3.bloodgroup="B+"
        blood3.save()        

        blood4=models.Stock()
        blood4.bloodgroup="B-"
        blood4.save()

        blood5=models.Stock()
        blood5.bloodgroup="AB+"
        blood5.save()

        blood6=models.Stock()
        blood6.bloodgroup="AB-"
        blood6.save()

        blood7=models.Stock()
        blood7.bloodgroup="O+"
        blood7.save()

        blood8=models.Stock()
        blood8.bloodgroup="O-"
        blood8.save()

    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')  
    return render(request,'blood/index2.html')

def is_donor(user):
    return user.groups.filter(name='DONOR').exists()

def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


def afterlogin_view(request):
    if is_donor(request.user):      
        return redirect('donor/donor-dashboard')
                
    elif is_patient(request.user):
        return redirect('patient/patient-dashboard')
    else:
        return redirect('admin-dashboard')

@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    totalunit=models.Stock.objects.aggregate(Sum('unit'))
    dict={

        'A1':models.Stock.objects.get(bloodgroup="A+"),
        'A2':models.Stock.objects.get(bloodgroup="A-"),
        'B1':models.Stock.objects.get(bloodgroup="B+"),
        'B2':models.Stock.objects.get(bloodgroup="B-"),
        'AB1':models.Stock.objects.get(bloodgroup="AB+"),
        'AB2':models.Stock.objects.get(bloodgroup="AB-"),
        'O1':models.Stock.objects.get(bloodgroup="O+"),
        'O2':models.Stock.objects.get(bloodgroup="O-"),
        'totaldonors':dmodels.Donor.objects.all().count(),
        'totalbloodunit':totalunit['unit__sum'],
        'totalrequest':models.BloodRequest.objects.all().count(),
        'totalapprovedrequest':models.BloodRequest.objects.all().filter(status='Approved').count()
    }
    return render(request,'blood/admin_dashboard.html',context=dict)

@login_required(login_url='adminlogin')
def admin_blood_view(request):
    dict={
        'bloodForm':forms.BloodForm(),
        'A1':models.Stock.objects.get(bloodgroup="A+"),
        'A2':models.Stock.objects.get(bloodgroup="A-"),
        'B1':models.Stock.objects.get(bloodgroup="B+"),
        'B2':models.Stock.objects.get(bloodgroup="B-"),
        'AB1':models.Stock.objects.get(bloodgroup="AB+"),
        'AB2':models.Stock.objects.get(bloodgroup="AB-"),
        'O1':models.Stock.objects.get(bloodgroup="O+"),
        'O2':models.Stock.objects.get(bloodgroup="O-"),
    }
    if request.method=='POST':
        bloodForm=forms.BloodForm(request.POST)
        if bloodForm.is_valid() :        
            bloodgroup=bloodForm.cleaned_data['bloodgroup']
            stock=models.Stock.objects.get(bloodgroup=bloodgroup)
            stock.unit=bloodForm.cleaned_data['unit']
            stock.save()
        return HttpResponseRedirect('admin-blood')
    return render(request,'blood/admin_blood.html',context=dict)


@login_required(login_url='adminlogin')
def admin_donor_view(request):
    donors=dmodels.Donor.objects.all()
    return render(request,'blood/admin_donor.html',{'donors':donors})

@login_required(login_url='adminlogin')
def update_donor_view(request,pk):
    donor=dmodels.Donor.objects.get(id=pk)
    user=dmodels.User.objects.get(id=donor.user_id)
    userForm=dforms.DonorUserForm(instance=user)
    donorForm=dforms.DonorForm(request.FILES,instance=donor)
    mydict={'userForm':userForm,'donorForm':donorForm}
    if request.method=='POST':
        userForm=dforms.DonorUserForm(request.POST,instance=user)
        donorForm=dforms.DonorForm(request.POST,request.FILES,instance=donor)
        if userForm.is_valid() and donorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            donor.save()
            return redirect('admin-donor')
    return render(request,'blood/update_donor.html',context=mydict)


@login_required(login_url='adminlogin')
def delete_donor_view(request,pk):
    donor=dmodels.Donor.objects.get(id=pk)
    user=User.objects.get(id=donor.user_id)
    user.delete()
    donor.delete()
    return HttpResponseRedirect('/admin-donor')

@login_required(login_url='adminlogin')
def admin_patient_view(request):
    patients=pmodels.Patient.objects.all()
    return render(request,'blood/admin_patient.html',{'patients':patients})


@login_required(login_url='adminlogin')
def update_patient_view(request,pk):
    patient=pmodels.Patient.objects.get(id=pk)
    user=pmodels.User.objects.get(id=patient.user_id)
    userForm=pforms.PatientUserForm(instance=user)
    patientForm=pforms.PatientForm(request.FILES,instance=patient)
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=pforms.PatientUserForm(request.POST,instance=user)
        patientForm=pforms.PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.bloodgroup=patientForm.cleaned_data['bloodgroup']
            patient.save()
            return redirect('admin-patient')
    return render(request,'blood/update_patient.html',context=mydict)


@login_required(login_url='adminlogin')
def delete_patient_view(request,pk):
    patient=pmodels.Patient.objects.get(id=pk)
    user=User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return HttpResponseRedirect('/admin-patient')

@login_required(login_url='adminlogin')
def admin_request_view(request):
    requests=models.BloodRequest.objects.all()
    return render(request,'blood/admin_request.html',{'requests':requests})

@login_required(login_url='adminlogin')
def admin_request_history_view(request):
    requests=models.BloodRequest.objects.all().exclude(status='Pending')
        # Count requests by status
    approved_count = requests.filter(status='Approved').count()
    rejected_count = requests.filter(status='Rejected').count()
    
    # You can add more status counts if needed
    
    context = {
        'requests': requests,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_count': requests.count(),  # Optional: total non-pending requests
    }
    return render(request,'blood/admin_request_history.html',{'requests':requests})
    
@login_required(login_url='adminlogin')
def admin_donation_view(request):
    donations=dmodels.BloodDonate.objects.all()
    return render(request,'blood/admin_donation.html',{'donations':donations})

@login_required(login_url='adminlogin')
def update_approve_status_view(request, pk):
    from blood.email_utils import send_patient_request_approved, send_patient_request_unavailable

    req = models.BloodRequest.objects.get(id=pk)
    message = None
    bloodgroup = req.bloodgroup
    unit = req.unit
    stock = models.Stock.objects.get(bloodgroup=bloodgroup)

    if stock.unit >= unit:
        stock.unit -= unit
        stock.save()
        req.status = "Approved"
        req.save()

        if req.request_by_patient:
            print(f"✅ Sending approval email to {req.request_by_patient}")
            try:
                send_patient_request_approved(req.request_by_patient, req)
            except Exception as e:
                print(f"❌ Error sending approval email: {e}")
        
    else:
        message = f"Stock does not have enough blood to approve this request. Only {stock.unit} unit(s) available."
        req.status = "Rejected"
        req.save()

        if req.request_by_patient:
            print(f"❗ Sending unavailability email to {req.request_by_patient}")
            try:
                send_patient_request_unavailable(req.request_by_patient, req)
            except Exception as e:
                print(f"❌ Error sending unavailability email: {e}")
            return render(request, 'blood/admin_request.html', {'requests': models.BloodRequest.objects.all(), 'message': message})

    return render(request, 'blood/admin_request.html', {'requests': models.BloodRequest.objects.filter(status='Pending'), 'message': message})



#view 2

@login_required(login_url='adminlogin')
def update_reject_status_view(request, pk):
    from blood.email_utils import send_patient_request_unavailable

    req = models.BloodRequest.objects.get(id=pk)
    req.status = "Rejected"
    req.save()

    if req.request_by_patient:
        print(f"❗ Sending rejection email to {req.request_by_patient}")
        try:
            send_patient_request_unavailable(req.request_by_patient, req)
        except Exception as e:
            print(f"❌ Error sending rejection email: {e}")

    return HttpResponseRedirect('/admin-request')


@login_required(login_url='adminlogin')
def approve_donation_view(request,pk):
    from blood.email_utils import send_donation_successful
    donation=dmodels.BloodDonate.objects.get(id=pk)
    donation_blood_group=donation.bloodgroup
    donation_blood_unit=donation.unit

    stock=models.Stock.objects.get(bloodgroup=donation_blood_group)
    stock.unit=stock.unit+donation_blood_unit
    stock.save()

    donation.status='Approved'
    donation.health_check_passed = True
    donation.save()

    # Send success email
    donor = donation.donor
    send_donation_successful(donor, donation)
    return HttpResponseRedirect('/admin-donation')


@login_required(login_url='adminlogin')
def reject_donation_view(request,pk):
    from blood.email_utils import send_donation_failed
    donation=dmodels.BloodDonate.objects.get(id=pk)
    donation.status='Rejected'
    donation.health_check_passed = False
    donation.save()

    # Send rejection email
    donor = donation.donor
    send_donation_failed(donor)
    return HttpResponseRedirect('/admin-donation')


def blood_bank_overview(request):
    blood_data = models.Stock.objects.all()  # Or filter as required
    context = {'blood_data': blood_data}
    return render(request, 'blood/overview.html', context)

# mod 1 
def index_view(request):
    totalunit = models.Stock.objects.aggregate(Sum('unit'))
    dict = {
        'A1': models.Stock.objects.get(bloodgroup="A+"),
        'A2': models.Stock.objects.get(bloodgroup="A-"),
        'B1': models.Stock.objects.get(bloodgroup="B+"),
        'B2': models.Stock.objects.get(bloodgroup="B-"),
        'AB1': models.Stock.objects.get(bloodgroup="AB+"),
        'AB2': models.Stock.objects.get(bloodgroup="AB-"),
        'O1': models.Stock.objects.get(bloodgroup="O+"),
        'O2': models.Stock.objects.get(bloodgroup="O-"),
        'totaldonors': dmodels.Donor.objects.all().count(),
        'totalbloodunit': totalunit['unit__sum'],
        'totalrequest': models.BloodRequest.objects.all().count(),
        'totalapprovedrequest': models.BloodRequest.objects.all().filter(status='Approved').count()
    }
    return render(request, 'blood/index2.html', context=dict)



# email mods 
def admin_emails(request):
    donors = Donor.objects.all()
    patients = Patient.objects.all()
    

    # Initialize counts
    blood_counts = {
        'A_plus': Donor.objects.filter(bloodgroup='A+').count(),
        'A_minus': Donor.objects.filter(bloodgroup='A-').count(),
        'B_plus': Donor.objects.filter(bloodgroup='B+').count(),
        'B_minus': Donor.objects.filter(bloodgroup='B-').count(),
        'AB_plus': Donor.objects.filter(bloodgroup='AB+').count(),
        'AB_minus': Donor.objects.filter(bloodgroup='AB-').count(),
        'O_plus': Donor.objects.filter(bloodgroup='O+').count(),
        'O_minus': Donor.objects.filter(bloodgroup='O-').count(),
    }

    eligible_counts = {}
    three_months_ago = datetime.now().date() - timedelta(days=90)

    for blood_group in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
        key = blood_group.replace('+', '_plus').replace('-', '_minus')
        eligible_counts[key] = Donor.objects.filter(
            status='APPROVED',
            bloodgroup=blood_group,
            last_donation_date__lt=three_months_ago
        ).count()

    eligible_donors = Donor.objects.filter(
        status='APPROVED',
        last_donation_date__lt=three_months_ago
    )

    urgent_requests = BloodRequest.objects.filter(
        is_urgent=True,
        status='PENDING'
    ).count()

    email_campaigns = EmailCampaign.objects.all().order_by('-date_sent')[:10]
    
    return render(request, 'blood/admin_emails.html', {
        'donors': donors,
        'patients': patients,
        'blood_counts_json': mark_safe(json.dumps(blood_counts)),
        'eligible_counts_json': mark_safe(json.dumps(eligible_counts)),
        'eligible_donors': eligible_donors,
        'urgent_requests': urgent_requests,
        'email_campaigns': email_campaigns,
    })

# def compose_email(request):
#     """View for composing an email and selecting recipients"""
#     if request.method == 'POST':
#         recipient_type = request.POST.get('recipient_type')
#         blood_group = request.POST.get('blood_group', '')
#         subject = request.POST.get('subject')
#         message = request.POST.get('message')

#         recipients = get_recipient_list(recipient_type, blood_group)

#         # Convert recipients to a list and remove None values
#         recipient_list = [email for email in recipients if email]

#         # Display only the first 5 recipients in the preview
#         recipient_display = ", ".join(recipient_list[:5])
#         if len(recipient_list) > 5:
#             recipient_display += f" and {len(recipient_list) - 5} more"

#         # Pass recipient list as JSON for the preview page
#         return render(request, 'blood/email_preview.html', {
#             'recipient': recipient_display,
#             'recipient_list': json.dumps(recipient_list),
#             'subject': subject,
#             'message': message
#         })

#     return render(request, 'blood/compose_email.html')

def compose_email(request):
    """View for composing an email, previewing it, and selecting recipients."""
    if request.method == 'POST':
        recipient_type = request.POST.get('recipient_type')
        blood_group = request.POST.get('blood_group', '')
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not recipient_type or not subject or not message:
            messages.error(request, "Please fill in all required fields.")
            return redirect('compose_email')

        # Get recipients and filter out invalid ones
        recipients = get_recipient_list(recipient_type, blood_group)
        recipient_list = [email for email in recipients if email]

        if not recipient_list:
            messages.warning(request, "No recipients found for the selected criteria.")
            return redirect('compose_email')

        # Limit the preview display
        preview_recipients = ", ".join(recipient_list[:5])
        if len(recipient_list) > 5:
            preview_recipients += f" and {len(recipient_list) - 5} more"

        context = {
            'recipient': preview_recipients,
            'recipient_list': json.dumps(recipient_list),
            'subject': subject,
            'message': message,
            'recipient_type': recipient_type, 
        }

        return render(request, 'blood/email_preview.html', context)

    return render(request, 'blood/compose_email.html')



def send_email(request):
    """View for sending emails after preview confirmation"""
    if request.method == 'POST':
        recipient_list = json.loads(request.POST.get('recipient_list', '[]'))
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        recipient_type = request.POST.get('recipient_type', 'custom')

        print("Submitted recipient list:", recipient_list)
        print("Subject:", subject)
        print("Message:", message)


        logger.info(f"Starting email send to {len(recipient_list)} recipients of type {recipient_type}")
        
        try:
            result = send_email_batch(subject, message, recipient_list)
            
            if result['failed_recipients']:
                logger.warning(f"Email send partially succeeded - {result['success_count']} sent, {len(result['failed_recipients'])} failed")
            else:
                logger.info(f"Successfully sent all {result['success_count']} emails")

            # Log email campaign
            campaign = EmailCampaign.objects.create(
                subject=subject,
                message=message,
                recipient_type=recipient_type,
                recipient_count=len(recipient_list),
                sent_by=request.user,
                success_count=result['success_count'],
                failed_count=len(result['failed_recipients'])
            )
            logger.info(f"Logged email campaign #{campaign.id}")

            if result['failed_recipients']:
                messages.warning(request, f'Email sent to {result["success_count"]} recipients, but failed for {len(result["failed_recipients"])}')
            else:
                messages.success(request, f'Email successfully sent to {result["success_count"]} recipients.')
                
        except Exception as e:
            logger.error(f"Email sending failed completely: {str(e)}", exc_info=True)
            messages.error(request, f'Failed to send email: {str(e)}')

        return redirect('admin_emails')

    logger.debug("Rendering compose email form")
    return redirect('compose_email')

def get_recipient_list(recipient_type, blood_group):
    """Helper function to fetch recipients based on selected criteria"""
    if recipient_type == 'all_donors':
        # Remove status filter or use correct status value
        return Donor.objects.all().values_list('email', flat=True)
    elif recipient_type == 'all_patients':
        return Patient.objects.values_list('email', flat=True)
    elif recipient_type == 'blood_group_donors' and blood_group:
        # Remove status filter or use correct status value
        return Donor.objects.filter(bloodgroup=blood_group).values_list('email', flat=True)
    elif recipient_type == 'eligible_donors':
        three_months_ago = timezone.now().date() - timedelta(days=90)
        # Include donors with no last_donation_date (None) as eligible
        return Donor.objects.filter(
            Q(last_donation_date__lt=three_months_ago) | 
            Q(last_donation_date__isnull=True)
        ).values_list('email', flat=True)
    return []


def send_email_batch(subject, message, recipient_list):
    """Sends emails in batches to prevent failures with large lists"""
    from blood.email_utils import validate_email_address
    from time import sleep
    import smtplib
    
    connection = get_connection()
    failed_recipients = []
    success_count = 0
    batch_size = 5  # Reduced batch size for better reliability
    delay = 5  # Increased delay between batches
    
    logger.info(f"Starting batch email send to {len(recipient_list)} recipients")
    logger.debug(f"SMTP settings - Host: {settings.EMAIL_HOST}, Port: {settings.EMAIL_PORT}")
    
    # Filter out None/empty emails
    valid_recipients = [email for email in recipient_list if email and validate_email_address(email)]
    logger.debug(f"Filtered to {len(valid_recipients)} valid email addresses")
    
    for i in range(0, len(valid_recipients), batch_size):
        batch = valid_recipients[i:i + batch_size]
        batch_emails = []
        
        logger.debug(f"Processing batch {i//batch_size + 1} with {len(batch)} emails")
        
        for recipient in batch:
            try:
                # Replace template placeholders with actual values
                personalized_message = message.format(
                    name=recipient.split('@')[0],  # Use email prefix as name
                    donation_date=timezone.now().strftime('%Y-%m-%d %H:%M %Z'),
                    blood_group='Unknown',  # Would need donor data to populate
                    hospital_name='Chuka Blood Bank',
                    contact_number='+254 123 456 789'
                )
                
                email = EmailMessage(
                    subject,
                    personalized_message,
                    settings.EMAIL_HOST_USER,
                    [recipient],
                    connection=connection
                )
                batch_emails.append(email)
                logger.debug(f"Prepared email for {recipient}")
            except Exception as e:
                logger.error(f"Error preparing email for {recipient}: {str(e)}")
                failed_recipients.append(recipient)

        try:
            logger.debug("Opening SMTP connection...")
            connection.open()
            logger.debug(f"Sending {len(batch_emails)} emails in current batch")
            
            connection.send_messages(batch_emails)
            success_count += len(batch_emails)
            logger.info(f"Successfully sent batch of {len(batch_emails)} emails")
            
            sleep(delay)  # Add delay between batches
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending batch: {str(e)}")
            failed_recipients.extend(batch)
            
            # Attempt to reconnect
            try:
                logger.debug("Attempting to reconnect to SMTP server...")
                connection.close()
                connection.open()
            except Exception as e:
                logger.error(f"Failed to reconnect to SMTP server: {str(e)}")
        except Exception as e:
            logger.error(f"Error sending batch: {str(e)}", exc_info=True)
            failed_recipients.extend(batch)
        finally:
            try:
                connection.close()
            except:
                pass

    logger.info(f"Batch send completed - {success_count} succeeded, {len(failed_recipients)} failed")
    return {
        'success_count': success_count,
        'failed_recipients': failed_recipients,
        'total_recipients': len(recipient_list)
    }

def load_template(request):
    """API endpoint to load an email template"""
    template_name = request.GET.get('template')
    template_data = {
        'donation_reminder': {
            'subject': 'Blood Donation Reminder',
            'message': """Dear {name},

                We hope this email finds you well. According to our records, you are now eligible to donate blood again since your last donation date of {donation_date}.

                Your blood type {blood_group} is currently needed in our blood bank. Would you like to schedule your next donation?

                Thank you for your continued support in saving lives.

                Warm regards,
                {hospital_name} Blood Bank Team
                {contact_number}"""
                        },
        'blood_drive': {
            'subject': 'Upcoming Blood Drive Announcement',
            'message': """Dear {name},

                We are pleased to announce that {hospital_name} will be hosting a blood drive on {event_date} from {start_time} to {end_time}.

                As someone with {blood_group} blood type, your donation would be especially valuable. One donation can save up to three lives!

                Location: {location}
                Requirements: Valid ID, be well-rested and hydrated

                To schedule your appointment, please reply to this email or call us at {contact_number}.

                Thank you for your support in our mission to maintain adequate blood supplies for our community.

                Best regards,
                {hospital_name} Blood Bank Team"""
                        },
        # Add other templates here
    }
    
    return JsonResponse(template_data.get(template_name, {'subject': '', 'message': ''}))