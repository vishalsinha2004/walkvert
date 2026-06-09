from rest_framework import serializers
from .models import Client, Campaign, PerformanceMetric, CampaignArea, ServiceItem

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
            'total_days', 'quantity_of_pieces', 'total_amount', 'budget', 'status', 
            'placement_locations', 'metrics', 'areas'
        ]

class ClientSerializer(serializers.ModelSerializer):
    campaigns = CampaignSerializer(many=True, read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'company_name', 'email', 'contact_phone', 'campaigns']


class ServiceItemSerializer(serializers.ModelSerializer):
    # Add this line to handle the image URL properly
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = ServiceItem
        # Use 'icon_url' instead of just 'icon'
        fields = ['id', 'name', 'icon_url', 'is_coming_soon']

    def get_icon_url(self, obj):
        if obj.icon:
            # This builds the full URL, e.g., http://localhost:8000/media/...
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.icon.url)
            return obj.icon.url
        return None