from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ClientDashboardViewSet, CampaignViewSet, RegisterClientView, VerifyOTPView, ServiceItemViewSet, GoogleLoginView

router = DefaultRouter()
router.register(r'dashboard', ClientDashboardViewSet, basename='dashboard')
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'services', ServiceItemViewSet, basename='service'),

urlpatterns = [
    # Auth & Registration
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterClientView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('google-login/', GoogleLoginView.as_view(), name='google_login'),
    # Core app routes
    path('', include(router.urls)),
]