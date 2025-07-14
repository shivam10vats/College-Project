from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string
from datetime import datetime, timedelta

# Create your models here.

class AdminRegistration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    hospital_name = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.hospital_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class AdminOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"OTP for {self.mobile_number}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def generate_otp(self):
        self.otp = ''.join(random.choices(string.digits, k=6))
        self.expires_at = timezone.now() + timedelta(minutes=10)
        self.save()

class PasswordReset(models.Model):
    RESET_TYPE_CHOICES = [
        ('mobile', 'Mobile Number'),
        ('email', 'Email'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    reset_type = models.CharField(max_length=10, choices=RESET_TYPE_CHOICES, default='mobile')
    token = models.CharField(max_length=100, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        if self.reset_type == 'mobile':
            return f"Password reset for {self.mobile_number}"
        else:
            return f"Password reset for {self.email}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def generate_token(self):
        self.token = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
        self.expires_at = timezone.now() + timedelta(hours=24)
        self.save()

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)  # Change from IntegerField to CharField

    def __str__(self):
        return self.name
    
class Patient(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    mobile_number = models.IntegerField(null=True)
    address = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
    
class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    def __str__(self):
        return f"{self.patient.name} - {self.doctor.name} on {self.appointment_date} at {self.appointment_time}"
