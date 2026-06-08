from django.db import models
from django.contrib.auth.models import User
import random
from django.utils import timezone
from datetime import timedelta

class Client(models.Model):
        # Linking to Django's built-in User model handles authentication seamlessly
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    company_name = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name

class Campaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='campaigns')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Where the ad is running (e.g., "Billboard A", "Digital Screen B")
    placement_locations = models.CharField(max_length=500, help_text="Comma separated locations")

    def __str__(self):
        return f"{self.title} ({self.client.company_name})"

class PerformanceMetric(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='metrics')
    date = models.DateField()
    impressions = models.PositiveIntegerField(default=0)
    clicks_or_interactions = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, help_text="Admin notes on daily performance")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensures only one metric entry per campaign per day
        unique_together = ['campaign', 'date']

    def __str__(self):
        return f"{self.campaign.title} - {self.date}"
    


class EmailOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_new_otp(self):
        # Generate a random 6-digit string
        self.otp_code = str(random.randint(100000, 999999))
        self.created_at = timezone.now()
        self.save()
        return self.otp_code

    def is_valid(self):
        # Enforce a 10-minute expiration window
        return timezone.now() <= self.created_at + timedelta(minutes=10)