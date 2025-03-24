from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from donor.models import Donor

class Patient(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/Patient/',null=True,blank=True)

    age=models.PositiveIntegerField()
    bloodgroup=models.CharField(max_length=10)
    disease=models.CharField(max_length=100)
    doctorname=models.CharField(max_length=50)

    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    email = models.EmailField(max_length=100, null=True, blank=True)  # New field
    assigned_donor = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_patients')

    property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_instance(self):
        return self
    def __str__(self):
        return self.user.first_name