from django.db import models
from patient import models as pmodels
from donor import models as dmodels

from django.contrib.auth.models import User
from datetime import datetime, timedelta

class Stock(models.Model):
    bloodgroup=models.CharField(max_length=10)
    unit=models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.bloodgroup

class BloodRequest(models.Model):
    request_by_patient=models.ForeignKey(pmodels.Patient,null=True,on_delete=models.CASCADE)
    request_by_donor=models.ForeignKey(dmodels.Donor,null=True,on_delete=models.CASCADE)
    patient_name=models.CharField(max_length=30)
    patient_age=models.PositiveIntegerField()
    reason=models.CharField(max_length=500)
    bloodgroup=models.CharField(max_length=10)
    unit=models.PositiveIntegerField(default=0)
    is_urgent = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default="PENDING", 
                             choices=(('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')))
    date=models.DateField(auto_now=True)
    def __str__(self):
        return self.bloodgroup

class EmailCampaign(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    recipient_type = models.CharField(max_length=50)
    recipient_count = models.IntegerField(default=0)
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_sent = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.subject       