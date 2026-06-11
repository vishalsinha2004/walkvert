from django.contrib import admin
from .models import Client, Campaign, PerformanceMetric, CampaignArea, ServiceItem, Booking

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

@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_coming_soon', 'created_at')
    list_filter = ('is_coming_soon',)
    search_fields = ('name',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # 1. What columns to show in the main table list
    list_display = ('id', 'name', 'get_user_email', 'get_service_name', 'phone', 'created_at')
    
    # 2. Add filters and search to easily find orders
    list_filter = ('created_at', 'service')
    search_fields = ('name', 'phone', 'user__email', 'requirement')
    
    # 3. Make ALL fields read-only when you click into a specific order
    readonly_fields = ('user', 'get_user_email', 'service', 'name', 'phone', 'requirement', 'created_at')

    # Custom function to pull the email from the linked User account
    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Account Email'

    # Custom function to show the service name nicely
    def get_service_name(self, obj):
        return obj.service.name
    get_service_name.short_description = 'Service Requested'

    # ==========================================
    # PREVENT ADMIN FROM ADDING/EDITING BOOKINGS
    # ==========================================
    
    def has_add_permission(self, request):
        # Removes the "Add Booking" button in the admin panel
        return False

    def has_change_permission(self, request, obj=None):
        # Prevents editing existing bookings (read-only mode)
        return False