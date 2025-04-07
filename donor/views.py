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
from django.utils import timezone
from datetime import datetime
from blood.email_utils import send_donation_request_received

def donor_signup_view(request):
    userForm=forms.DonorUserForm()
    donorForm=forms.DonorForm()
    mydict={'userForm':userForm,'donorForm':donorForm}
    if request.method=='POST':
        userForm=forms.DonorUserForm(request.POST)
        donorForm=forms.DonorForm(request.POST,request.FILES)
        if userForm.is_valid() and donorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            donor.save()
            my_donor_group = Group.objects.get_or_create(name='DONOR')
            my_donor_group[0].user_set.add(user)
        return HttpResponseRedirect('donorlogin')
    return render(request,'donor/donorsignup.html',context=mydict)


def donor_dashboard_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    dict={
        'requestpending': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Pending').count(),
        'requestapproved': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Approved').count(),
        'requestmade': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).count(),
        'requestrejected': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Rejected').count(),
        # manzee am smart af 
        'donor': donor, 
    }
    donor= models.Donor.objects.get(user_id=request.user.id)
    return render(request,'donor/donor_dashboard.html',context=dict)



def donate_blood_view(request):
    donation_form = forms.DonationForm()

    if request.method == 'POST':
        donation_form = forms.DonationForm(request.POST)
        if donation_form.is_valid():
            blood_donate = donation_form.save(commit=False)
            blood_donate.bloodgroup = donation_form.cleaned_data['bloodgroup']
            
            donor = models.Donor.objects.get(user_id=request.user.id)
            blood_donate.donor = donor

            # Update last donation date dynamically
            donor.last_donation_date = timezone.now().date() - timedelta(days=90)
            donor.save()

            blood_donate.save()

            # Send email notification
            send_donation_request_received(donor)

            return HttpResponseRedirect('donation-history')  

    return render(request, 'donor/donate_blood.html', {'donation_form': donation_form})

def donation_history_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    donations=models.BloodDonate.objects.all().filter(donor=donor)
    return render(request,'donor/donation_history.html',{'donations':donations})

def make_request_view(request):
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            blood_request.bloodgroup=request_form.cleaned_data['bloodgroup']
            donor= models.Donor.objects.get(user_id=request.user.id)
            blood_request.request_by_donor=donor
            blood_request.save()
            return HttpResponseRedirect('request-history')  
    return render(request,'donor/makerequest.html',{'request_form':request_form})

def request_history_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    blood_request=bmodels.BloodRequest.objects.all().filter(request_by_donor=donor)
    return render(request,'donor/request_history.html',{'blood_request':blood_request})

def donor_view(request):
    donors = models.Donor.objects.all()
    return render(request, 'blood/index2.html', {'donors': donors})

@login_required(login_url='donorlogin')
def update_notification_settings(request):
    if request.method == 'POST':
        # Get the donor instance
        # donor = models.Donor.objects.get(user_id=request.user.id)
        try:
            donor = models.Donor.objects.get(user_id=request.user.id)
        except models.Donor.DoesNotExist:
    # Handle the exception by creating a new Donor object or providing an error message
            donor = models.Donor(user_id=request.user.id)
            donor.save()
            
        # Update email
        email = request.POST.get('email')
        if email:
            # Update both user email and donor email
            request.user.email = email
            request.user.save()
            donor.email = email
            donor.save()
            
        # You could also store preference settings in a new model if needed
        
        return redirect('donor-dashboard')
    return redirect('donor-dashboard')