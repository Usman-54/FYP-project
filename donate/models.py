from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver
# Create your models here.
class Adminprofile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact= models.CharField( max_length=50, null=True)
    address = models.CharField(max_length=150, null=True)
    adminpic = models.FileField(upload_to='admin_images/', null=True, blank=True)
    regdate = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.user.username

class Donor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contact= models.CharField( max_length=50, null=True)
    userpic = models.FileField(null=True)
    address = models.CharField(max_length=150, null=True)
    regdate = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.user.username


class Donation(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    donation_type = models.CharField(max_length=255)  # Store comma-separated values
    donation_image = models.ImageField(upload_to='donation_images/')
    collection_address = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Pending') 
    # payment methods 
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    payment_status = models.CharField(max_length=50, default='Unpaid')  # Paid, Failed, Unpaid

    def __str__(self):
        return f"{self.donor.username} - {self.donation_type}"

    
class Volunteer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact= models.CharField( max_length=50, null=True)
    # Cnic = models.CharField(max_length=13, null=True, blank=True)
    address = models.CharField(max_length=150, null=True)
    userpic = models.FileField(null=True)
    regdate = models.DateField(auto_now_add=True)
    aboutme = models.CharField( max_length=100, null=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    def __str__(self):
        return self.user.username

@receiver(post_delete, sender=Volunteer)
def delete_user_with_volunteer(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()
    
class DonationArea(models.Model):
    areaname = models.CharField(max_length=150, null=True)
    description = models.CharField(max_length=300, null=True)
    volunteers = models.ManyToManyField('Volunteer', blank=True) 
    creationdate = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.areaname

class Beneficiary(models.Model):
    full_name = models.CharField(max_length=150)
    father_name = models.CharField(max_length=150, blank=True)
    contact_number = models.CharField(max_length=15)
    cnic = models.CharField(max_length=13, blank=True, null=True)
    family_members = models.IntegerField(blank=True, null=True)
    address = models.TextField()
    date_received = models.DateField(auto_now_add=True)
    STATUS_CHOICES = [
        ('Widow', 'Widow'),
        ('Orphan', 'Orphan'),
        ('Poor', 'Poor'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='poor',  blank=True)

    def __str__(self):
        return self.full_name
