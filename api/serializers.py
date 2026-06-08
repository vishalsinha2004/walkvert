from rest_framework import serializers
from .models import Client, Campaign, PerformanceMetric, CampaignArea

class PerformanceMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceMetric
        fields = ['id', 'date', 'impressions', 'clicks_or_interactions', 'notes']

class CampaignAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignArea
        fields = ['id', 'area_name', 'percentage']

class CampaignSerializer(serializers.ModelSerializer):
    metrics = PerformanceMetricSerializer(many=True, read_only=True)
    areas = CampaignAreaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Campaign
        fields = [
            'id', 'advertisement_title', 'description', 'start_date', 'end_date', 
            'total_days', 'quantity_of_pieces', 'budget', 'status', 
            'placement_locations', 'metrics', 'areas'
        ]

class ClientSerializer(serializers.ModelSerializer):
    campaigns = CampaignSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'company_name', 'contact_phone', 'campaigns']