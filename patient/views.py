from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from blood import forms as bforms
from blood import models as bmodels


def patient_signup_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        print(request.POST)  # Debugging: Ensure form data is received

        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.bloodgroup=patientForm.cleaned_data['bloodgroup']
            patient.save()
            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
        return HttpResponseRedirect('patientlogin')
    return render(request,'patient/patientsignup.html',context=mydict) 

def patient_dashboard_view(request):
    patient= models.Patient.objects.get(user_id=request.user.id)
    dict={
        'requestpending': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Pending').count(),
        'requestapproved': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Approved').count(),
        'requestmade': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).count(),
        'requestrejected': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Rejected').count(),
        'patient': patient,

    }
   
    return render(request,'patient/patient_dashboard.html',context=dict)

def make_request_view(request):
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            blood_request.bloodgroup=request_form.cleaned_data['bloodgroup']
            patient= models.Patient.objects.get(user_id=request.user.id)
            blood_request.request_by_patient=patient
            blood_request.save()

             # Check if blood is available
            from blood.models import Stock
            from blood.email_utils import send_patient_request_approved, send_patient_request_unavailable, send_urgent_request_to_donors
            
            stock = Stock.objects.get(bloodgroup=blood_request.bloodgroup)
            
            # Add a field to indicate urgency - you can add this to the form
            is_urgent = request.POST.get('is_urgent', False)
            
            if stock.unit >= blood_request.unit:
                # Blood is available - don't approve yet, wait for admin
                # But notify the patient it's likely to be approved
                send_patient_request_approved(patient, blood_request)
            else:
                # Blood unavailable
                send_patient_request_unavailable(patient, blood_request)
                
                # If urgent, notify matching donors
                if is_urgent:
                    donors_notified = send_urgent_request_to_donors(blood_request.bloodgroup, patient)

                
            
            return HttpResponseRedirect('my-request')  
    return render(request,'patient/makerequest.html',{'request_form':request_form})

def my_request_view(request):
    patient= models.Patient.objects.get(user_id=request.user.id)
    blood_request=bmodels.BloodRequest.objects.all().filter(request_by_patient=patient)
    return render(request,'patient/my_request.html',{'blood_request':blood_request})


@login_required(login_url='patientlogin')
def update_patient_notification_settings(request):
    if request.method == 'POST':
        # Get the patient instance
        try:
            patient = models.Patient.objects.get(user_id=request.user.id)
        except models.Patient.DoesNotExist:
            # Handle missing patient instance
            patient = models.Patient(user_id=request.user.id)
            patient.save()

        # Update email
        email = request.POST.get('email')
        if email:
            request.user.email = email
            request.user.save()
            patient.email = email
            patient.save()

        # Redirect to patient dashboard
        return redirect('patient-dashboard')

    return redirect('patient-dashboard')
