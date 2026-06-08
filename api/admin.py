from django.contrib import admin
from .models import Client, Campaign, PerformanceMetric, CampaignArea

class CampaignAreaInline(admin.TabularInline):
    model = CampaignArea
    extra = 1

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'created_at')
    search_fields = ('company_name', 'user__email')

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('advertisement_title', 'client', 'quantity_of_pieces', 'total_days', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'client')
    search_fields = ('advertisement_title', 'client__company_name')
    inlines = [CampaignAreaInline]

@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'date', 'impressions', 'clicks_or_interactions')
    list_filter = ('campaign', 'date')
    date_hierarchy = 'date'