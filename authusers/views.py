from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login
from .models import TemporaryUser, OTP, CustomerProfile

from .serializers import (
    UserRegistrationSerializer,
    OTPVerificationSerializer,
    PasswordLoginSerializer,
    OTPLoginSerializer,
    VendorProfileSerializer,
    CustomerProfileSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from .models import VendorProfile
from .models import User


# ================================
# Helper Function for JWT Tokens
# ================================
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# ================================
# User Registration View
# ================================
class UserRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful. OTP sent to email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ================================
# OTP Verification View
# ================================
class OTPVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.create_user(serializer.validated_data)
            tokens = get_tokens_for_user(user)
            return Response({"message": "OTP verified successfully.", "tokens": tokens}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ================================
# Password Login View
# ================================
class PasswordLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            tokens = get_tokens_for_user(user)
            login(request, user)
            return Response({"message": "Login successful.", "tokens": tokens}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

# ================================
# OTP Login View
# ================================
class OTPLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPLoginSerializer(data=request.data)
        if serializer.is_valid():
            serializer.send_login_otp()
            return Response({"message": "OTP sent to email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ================================
# OTP Login Verification View
# ================================
class OTPLoginVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = get_object_or_404(User, email=email)
            tokens = get_tokens_for_user(user)
            return Response({"message": "OTP login successful.", "tokens": tokens}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ================================
# Vendor Profile View
# ================================
# ================================
# Vendor Profile View
# ================================
class VendorProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Correctly fetch the VendorProfile object
        vendor_profile = get_object_or_404(VendorProfile, user=request.user)
        serializer = VendorProfileSerializer(vendor_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        # Correctly fetch the VendorProfile object
        vendor_profile = get_object_or_404(VendorProfile, user=request.user)
        serializer = VendorProfileSerializer(vendor_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ================================
# Customer Profile View
# ================================
class CustomerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Access the related customer profile directly
            customer_profile = request.user.customer_profile
            serializer = CustomerProfileSerializer(customer_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomerProfile.DoesNotExist:
            return Response(
                {"error": "Customer profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def patch(self, request):
        try:
            # Access the related customer profile directly
            customer_profile = request.user.customer_profile
            serializer = CustomerProfileSerializer(
                customer_profile, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomerProfile.DoesNotExist:
            return Response(
                {"error": "Customer profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )






from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PasswordResetRequestSerializer

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from .serializers import PasswordResetConfirmSerializer

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the token to invalidate it
            return Response({"message": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token or logout failed."}, status=status.HTTP_400_BAD_REQUEST)






from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Address
from .serializers import AddressSerializer
from django.shortcuts import get_object_or_404

class AddressListCreateView(APIView):
    """
    View to list all addresses for the logged-in user and create new addresses.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all addresses for the current user.
        """
        addresses = Address.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new address for the current user.
        """
        serializer = AddressSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressDetailView(APIView):
    """
    View to retrieve, update, or delete a specific address for the logged-in user.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, user, pk):
        """
        Helper method to get an address or return 404.
        """
        return get_object_or_404(Address, user=user, pk=pk)

    def get(self, request, pk):
        """
        Retrieve a specific address by its ID.
        """
        address = self.get_object(request.user, pk)
        serializer = AddressSerializer(address)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Fully update an address.
        """
        address = self.get_object(request.user, pk)
        serializer = AddressSerializer(address, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """
        Partially update an address.
        """
        address = self.get_object(request.user, pk)
        serializer = AddressSerializer(address, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a specific address.
        """
        address = self.get_object(request.user, pk)
        address.delete()
        return Response({"message": "Address deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
