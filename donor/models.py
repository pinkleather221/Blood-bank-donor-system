from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Donor(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    # profile_pic= models.ImageField(upload_to='profile_pic/Donor/',null=True,blank=True)
    profile_pic= models.ImageField(upload_to='profile_pic/Donor/')
    bloodgroup=models.CharField(max_length=10)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    email = models.EmailField(max_length=100, null=True, blank=True)  # New field
    last_donation_date = models.DateTimeField(null=True, blank=True)  # Track last donation
    

   
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_instance(self):
        return self
    def __str__(self):
        return self.user.first_name

class BloodDonate(models.Model): 
    donor=models.ForeignKey(Donor,on_delete=models.CASCADE)   
    disease=models.CharField(max_length=100,default="Nothing")
    age=models.PositiveIntegerField()
    bloodgroup=models.CharField(max_length=10)
    unit=models.PositiveIntegerField(default=0)
    status=models.CharField(max_length=20,default="Pending")
    date=models.DateField(auto_now=True)
    health_check_passed = models.BooleanField(default=False)  # New field
    
    def __str__(self):
        return self.donor