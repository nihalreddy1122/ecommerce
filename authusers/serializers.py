from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, TemporaryUser, VendorProfile, CustomerProfile, OTP
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .tasks import send_email_task  # Ensure Celery task is imported
from datetime import timedelta
from vendors.models import VendorDetails


# ================================
# User Registration Serializer
# ================================
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = TemporaryUser
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'user_type', 'password']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])  # Hash the password
        otp = OTP.objects.create(email=validated_data['email'], otp=str(self.generate_otp()))
        validated_data['otp'] = otp.otp
        # Save temporary user
        temp_user = TemporaryUser.objects.create(**validated_data)
        self.send_otp_email(temp_user.email, otp.otp, temp_user.first_name)  # Include user's name
        return temp_user

    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP."""
        import random
        return random.randint(100000, 999999)

    @staticmethod
    def send_otp_email(email, otp, first_name):
        """Send the OTP via email using an HTML template."""
        subject = "Welcome to HIDDEN STORES - Your OTP Code"
        plain_message = f"Your OTP is {otp}. It is valid for 5 minutes."
        html_message = render_to_string('emails/register_email.html', {
            'otp': otp,
            'user': {'first_name': first_name},
            'site_url': 'https://hiddenstores.com',
        })
        send_email_task.delay(subject, plain_message, "no-reply@hiddenstores.com", [email], html_message=html_message)  # Use Celery task

# ================================
# OTP Verification Serializer
# ================================
class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            otp_instance = OTP.objects.filter(email=data['email']).latest('created_at')
        except OTP.DoesNotExist:
            raise serializers.ValidationError("No OTP found for this email.")

        if otp_instance.otp != data['otp']:
            raise serializers.ValidationError("Invalid OTP.")

        if otp_instance.is_expired():
            raise serializers.ValidationError("OTP has expired.")

        return data

    def create_user(self, validated_data):
        email = validated_data['email']
        temp_user = TemporaryUser.objects.get(email=email)

        # Move data from TemporaryUser to User
        user = User.objects.create(
            email=temp_user.email,
            first_name=temp_user.first_name,
            last_name=temp_user.last_name,
            phone_number=temp_user.phone_number,
            user_type=temp_user.user_type,
            password=temp_user.password,
        )

        # Create Profile
        if user.user_type == 'vendor':
            VendorProfile.objects.create(user=user)
            VendorDetails.objects.create(user=user)
        elif user.user_type == 'customer':
            CustomerProfile.objects.create(user=user)

        temp_user.delete()  # Remove TemporaryUser after successful registration
        return user

# ================================
# Password Login Serializer
# ================================
class PasswordLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")
        return user

# ================================
# OTP Login Serializer
# ================================
class OTPLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user is associated with this email.")
        return value

    def send_login_otp(self):
        email = self.validated_data['email']
        otp = OTP.objects.create(email=email, otp=str(self.generate_otp()))
        user = User.objects.get(email=email)
        self.send_otp_email(email, otp.otp, user.first_name)

    @staticmethod
    def generate_otp():
        import random
        return random.randint(100000, 999999)

    @staticmethod
    def send_otp_email(email, otp, first_name):
        subject = "HIDDEN STORES - Your Login OTP Code"
        plain_message = f"Your OTP is {otp}. It is valid for 5 minutes."
        html_message = render_to_string('emails/login_email.html', {
            'otp': otp,
            'user': {'first_name': first_name},
            'site_url': 'https://hiddenstores.com',
        })
        send_email_task.delay(subject, plain_message, "no-reply@hiddenstores.com", [email], html_message=html_message)  # Use Celery task

# ================================
# VendorProfile Serializer
# ================================
class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = [ 'shop_address']

# ================================
# CustomerProfile Serializer
# ================================
class CustomerProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerProfile
        fields = ['user','date_of_birth', 'gender']

    def get_user(self, obj):
        """
        Return the related User fields as a dictionary.
        """
        user = obj.user
        return {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'email': user.email,
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email']



from rest_framework import serializers
from .models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.conf import settings

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        """Ensure the email exists in the system."""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value

    def save(self):
        email = self.validated_data['email']
        otp_code = str(self.generate_otp())
        OTP.objects.create(email=email, otp=otp_code)

        # Send OTP via email
        subject = "Reset Your Password - Hidden Stores"
        html_message = render_to_string('emails/password_reset_email.html', {
            'otp': otp_code,
        })
        send_email_task.delay(subject, f"Your OTP is {otp_code}.", "no-reply@hiddenstores.com", [email], html_message=html_message)

    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP."""
        import random
        return random.randint(100000, 999999)



class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate OTP and its expiration."""
        try:
            otp_instance = OTP.objects.filter(email=data['email']).latest('created_at')
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP or email.")

        if otp_instance.otp != data['otp']:
            raise serializers.ValidationError("Invalid OTP.")

        if otp_instance.is_expired():
            raise serializers.ValidationError("OTP has expired.")

        return data

    def save(self):
        """Reset the user's password."""
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']

        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        # Delete OTP after successful password reset
        OTP.objects.filter(email=email).delete()






from rest_framework import serializers
from .models import Address

class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for managing user addresses.
    """

    class Meta:
        model = Address
        fields = [
            'id',
            'full_name',
            'phone_number',
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'postal_code',
            'country',
            'is_default',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Custom validation for phone number and other fields if needed.
        """
        if len(data.get('phone_number', '')) < 10:
            raise serializers.ValidationError({"phone_number": "Phone number must be at least 10 digits."})
        return data

    def create(self, validated_data):
        """
        Save new address and handle default address logic.
        """
        user = self.context['request'].user
        address = Address.objects.create(user=user, **validated_data)
        return address

    def update(self, instance, validated_data):
        """
        Update address and ensure only one default address.
        """
        if validated_data.get('is_default', False):
            Address.objects.filter(user=instance.user, is_default=True).update(is_default=False)
        return super().update(instance, validated_data)
