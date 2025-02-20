from django.contrib import admin
from .models import User, TemporaryUser, VendorProfile, CustomerProfile, OTP, Address

# ================================
# User Admin
# ================================
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'user_type', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('date_joined',)


# ================================
# TemporaryUser Admin
# ================================
@admin.register(TemporaryUser)
class TemporaryUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'user_type', 'created_at')
    list_filter = ('user_type', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)


# ================================
# VendorProfile Admin
# ================================
@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'shop_address', 'created_at')
    ordering = ('-created_at',)


# ================================
# CustomerProfile Admin
# ================================
@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date_of_birth', 'gender')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')


# ================================
# OTP Admin
# ================================
@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'otp', 'created_at')
    search_fields = ('email',)
    ordering = ('-created_at',)


# ================================
# Address Admin
# ================================
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'phone_number', 'city', 'state', 'country', 'is_default', 'created_at')
    list_filter = ('city', 'state', 'country', 'is_default')
    search_fields = ('user__email', 'full_name', 'phone_number', 'city', 'state', 'postal_code')
    ordering = ('-created_at',)
