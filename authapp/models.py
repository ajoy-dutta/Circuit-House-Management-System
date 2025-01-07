from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

# Users Table
class User(AbstractUser):
    ROLE_CHOICES = [
        ('NDC', 'NDC'),
        ('Assistant Accountant', 'Assistant Accountant'),
    ]
    role = models.CharField(max_length=40, choices=ROLE_CHOICES, default='Assistant Accountant', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='img/', blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='custom_user_set', 
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='custom_user_permissions_set', 
        blank=True
    )

    def save(self, *args, **kwargs):
        # If the user is a superuser, set their role to 'NDC' and is_approved to True
        if self.is_superuser:
            self.role = 'NDC'
            self.is_approved = True
        elif not self.role:  # If the role is not provided, assign the default 'Assistant Accountant'
            self.role = 'Assistant Accountant'
        super().save(*args, **kwargs)  # Call the original save method

    def __str__(self):
        return self.username

class StaffProfile(models.Model):
    name = models.CharField(max_length=255)
    picture = models.ImageField(upload_to='img/')
    designation = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    joining_date = models.DateField()
    ending_date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)


# Honour Board
class HonourBoard(models.Model):
    TYPE_CHOICES = [
        ('DC', 'DC'),
        ('NDC', 'NDC'),
    ]
    name = models.CharField(max_length=255)
    batch = models.CharField(max_length=50,null=True,blank=True)
    joining_date = models.DateField()
    ending_date = models.DateField(blank=True,null=True)
    photo = models.ImageField(upload_to='img/',blank=True,null=True)
    remarks = models.TextField(blank=True, null=True)
    designation_type = models.CharField(max_length=3, choices=TYPE_CHOICES, default='DC') 

    def __str__(self):
        return f"{self.name} - {self.designation_type}"
    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone=models.CharField(max_length=50,blank=True,null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name