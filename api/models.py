from django.db import models
from django.contrib.auth.models import User
import random
from django.utils import timezone
from datetime import timedelta

class Client(models.Model):
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
    advertisement_title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    
    total_days = models.PositiveIntegerField(help_text="Total number of days the ad will run", default=0)
    quantity_of_pieces = models.PositiveIntegerField(help_text="Total quantity of pieces/units", default=0)
    
    # NEW FIELD ADDED HERE:
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Total cost/amount for the campaign")
    
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    placement_locations = models.CharField(max_length=500, help_text="Comma separated locations")

    def __str__(self):
        return f"{self.advertisement_title} ({self.client.company_name})"

class CampaignArea(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='areas')
    area_name = models.CharField(max_length=100)
    percentage = models.PositiveIntegerField(help_text="Enter percentage (e.g., 40 for 40%)")

    def __str__(self):
        return f"{self.area_name} ({self.percentage}%) - {self.campaign.advertisement_title}"

class PerformanceMetric(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='metrics')
    date = models.DateField()
    impressions = models.PositiveIntegerField(default=0)
    clicks_or_interactions = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, help_text="Admin notes on daily performance")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['campaign', 'date']

    def __str__(self):
        return f"{self.campaign.advertisement_title} - {self.date}"

class EmailOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_new_otp(self):
        self.otp_code = str(random.randint(100000, 999999))
        self.created_at = timezone.now()
        self.save()
        return self.otp_code

    def is_valid(self):
        return timezone.now() <= self.created_at + timedelta(minutes=10)
    
class ServiceItem(models.Model):
    name = models.CharField(max_length=255, help_text="e.g., Plastic Bags, Paper Glass")
    icon = models.ImageField(upload_to='services/icons/', blank=True, null=True)
    is_coming_soon = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name