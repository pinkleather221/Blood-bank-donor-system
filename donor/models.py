from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

class Donor(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    # profile_pic= models.ImageField(upload_to='profile_pic/Donor/',null=True,blank=True)
    profile_pic= models.ImageField(upload_to='profile_pic/Donor/')
    bloodgroup=models.CharField(max_length=10)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    email = models.EmailField(max_length=100, null=True, blank=True)  # New field
    last_donation_date = models.DateTimeField(null=True, blank=True)  # Track last donation
    
    health_status = models.CharField(max_length=20, default='UNKNOWN', 
                                    choices=(('ELIGIBLE', 'Eligible'), 
                                            ('INELIGIBLE', 'Ineligible'), 
                                            ('UNKNOWN', 'Unknown')))
    status = models.CharField(max_length=20, default="PENDING", 
                             choices=(('PENDING', 'Pending'), ('APPROVED', 'Approved')))

    @property
    def is_eligible_to_donate(self):
        if not self.last_donation_date:
            return True
        three_months_ago = timezone.now().date() - timedelta(days=90)
        return self.last_donation_date.date() < three_months_ago and self.health_status == 'ELIGIBLE'
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
    health_check = models.CharField(max_length=20, default='PENDING', 
                                   choices=(('PENDING', 'Pending'), 
                                           ('PASSED', 'Passed'), 
                                           ('FAILED', 'Failed')))
    status = models.CharField(max_length=20, default="PENDING", 
                             choices=(('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')))
    
    def save(self, *args, **kwargs):
        # Update donor's last donation date when approved
        if self.status == 'APPROVED' and self.health_check == 'PASSED':
            self.donor.last_donation_date = self.donation_date
            self.donor.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.donor