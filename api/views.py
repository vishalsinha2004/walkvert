import os
import requests
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

# --- NEW GOOGLE IMPORTS ---
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# 🌟 UPDATED: Import the action decorator
from rest_framework.decorators import action

# 🌟 UPDATED: Ensure Booking and BookingSerializer are imported
from .models import Client, Campaign, EmailOTP, ServiceItem, Booking
from .serializers import ClientSerializer, CampaignSerializer, ServiceItemSerializer, BookingSerializer


# ==========================================
# CLIENT DASHBOARD VIEWS (Read-Only)
# ==========================================

class ClientDashboardViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Security: The logged-in user can ONLY retrieve their own client profile
        return Client.objects.filter(user=self.request.user)

class CampaignViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Security: The logged-in user can ONLY retrieve their own campaigns
        return Campaign.objects.filter(client__user=self.request.user)


# ==========================================
# REGISTRATION & OTP VERIFICATION VIEWS
# ==========================================

class RegisterClientView(APIView):
    # This endpoint must be open to unauthenticated users so they can sign up
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        company_name = request.data.get('company_name')

        if User.objects.filter(username=email).exists():
            return Response({'error': 'An account with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Create the user but mark them as INACTIVE until OTP is verified
        user = User.objects.create_user(username=email, email=email, password=password)
        user.is_active = False
        user.save()

        # 2. Create the associated Client profile
        Client.objects.create(user=user, company_name=company_name)

        # 3. Generate the OTP
        otp_device, created = EmailOTP.objects.get_or_create(user=user)
        otp_code = otp_device.generate_new_otp()

        # 4. Send the OTP via Brevo REST API
        raw_api_key = getattr(settings, 'BREVO_API_KEY', '')
        brevo_api_key = raw_api_key.strip() if raw_api_key else ''
        
        # --- Temporary clean debug lines ---
        url = "https://api.brevo.com/v3/smtp/email"
        
        payload = {
            "sender": {
                "name": "Walkvert",
                "email": "walkvert@gmail.com" # Must match your verified Brevo domain or your account email
            },
            "to": [
                {
                    "email": email,
                    "name": company_name
                }
            ],
            "subject": "Your Walkvert Verification Code",
            "htmlContent": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>Welcome to Walkvert</h2>
                    <p>Your verification code is: <strong style="font-size: 24px;">{otp_code}</strong></p>
                    <p>This code will expire in 10 minutes.</p>
                </div>
            """
        }
        
        headers = {
            "accept": "application/json",
            "api-key": brevo_api_key,
            "content-type": "application/json"
        }

        # Fire the request to Brevo
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status() 
        except requests.exceptions.RequestException as e:
            # --- NEW DEBUG LINES: Print the exact reason Brevo is angry ---
            print(f"BREVO EXPLANATION: {response.text}")
            
            # Delete the inactive user if the email fails so they can try again immediately
            user.delete()
            return Response({'error': 'Failed to send verification email. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_201_CREATED)


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')

        try:
            user = User.objects.get(username=email)
            otp_device = EmailOTP.objects.get(user=user)
        except (User.DoesNotExist, EmailOTP.DoesNotExist):
            return Response({'error': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the code
        if otp_device.otp_code != otp_code:
            return Response({'error': 'Incorrect verification code.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check expiration
        if not otp_device.is_valid():
            return Response({'error': 'Verification code has expired. Please register again.'}, status=status.HTTP_400_BAD_REQUEST)

        # 5. Success! Activate the user account
        user.is_active = True
        user.save()
        
        # 6. Delete the OTP device so the code cannot be reused
        otp_device.delete()

        # 7. Generate JWT Tokens so the frontend can instantly log them into the dashboard
        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'message': 'Account verified successfully.'
        }, status=status.HTTP_200_OK)


# ==========================================
# SERVICE ITEMS & BOOKING VIEW
# ==========================================

class ServiceItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceItem.objects.all().order_by('-created_at')
    serializer_class = ServiceItemSerializer
    permission_classes = [permissions.AllowAny] # Anyone can see the list of services

    # 🌟 NEW: Custom action for booking a specific service
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def book(self, request, pk=None):
        service = self.get_object() # Gets the specific service from the URL ID
        serializer = BookingSerializer(data=request.data)
        
        if serializer.is_valid():
            # Save the booking. request.user automatically provides the email.
            booking = serializer.save(user=request.user, service=service)
            
            # Fetch the authenticated user's email
            user_email = request.user.email
            
            # Optional: Here you can integrate Brevo to send an email notification to the Admin
            
            return Response({
                "message": "Booking successfully placed!",
                "user_email": user_email
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# GOOGLE AUTHENTICATION VIEW
# ==========================================

class GoogleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('credential')
        if not token:
            return Response({'error': 'No credential provided.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                getattr(settings, 'GOOGLE_CLIENT_ID', ''),
                clock_skew_in_seconds=10 # Allows up to 10 seconds of clock difference!
            )

            email = idinfo['email']
            name = idinfo.get('name', email.split('@')[0])

            # Check if user exists
            user = User.objects.filter(username=email).first()
            
            if not user:
                # If it's a new user (Sign Up), create User and Client profile
                user = User.objects.create_user(username=email, email=email)
                user.is_active = True  # Google verified the email automatically
                user.save()
                
                # Create Client profile using their Google name as company_name
                Client.objects.create(user=user, company_name=f"{name}'s Company")
            
            # If user exists but is inactive (e.g. abandoned standard signup), activate them
            if not user.is_active:
                user.is_active = True
                user.save()

            # Generate your app's JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'message': 'Google authentication successful.'
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            # THIS WILL PRINT THE EXACT REASON IN YOUR PYTHON TERMINAL
            print(f"GOOGLE VERIFICATION FAILED: {e}") 
            return Response({'error': 'Invalid Google token.'}, status=status.HTTP_400_BAD_REQUEST)