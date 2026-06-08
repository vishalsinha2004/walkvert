from rest_framework import serializers
from .models import Client, Campaign, PerformanceMetric

class PerformanceMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceMetric
        # Expose exactly what the client needs to see on their dashboard
        fields = ['id', 'date', 'impressions', 'clicks_or_interactions', 'notes']

class CampaignSerializer(serializers.ModelSerializer):
    # This automatically fetches all metrics associated with the campaign
    metrics = PerformanceMetricSerializer(many=True, read_only=True)
    
    class Meta:
        model = Campaign
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'budget', 'status', 'placement_locations', 'metrics']

class ClientSerializer(serializers.ModelSerializer):
    # This fetches all campaigns associated with the client
    campaigns = CampaignSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'company_name', 'contact_phone', 'campaigns']