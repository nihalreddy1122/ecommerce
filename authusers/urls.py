from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)

from .views import (
    UserRegistrationView,
    OTPVerificationView,
    PasswordLoginView,
    OTPLoginView,
    OTPLoginVerificationView,
    VendorProfileView,
    CustomerProfileView,
    PasswordResetRequestView, 
    PasswordResetConfirmView,
    LogoutView,
    AddressListCreateView, 
    AddressDetailView,
)

urlpatterns = [
    # Registration Endpoints
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('verify-otp/', OTPVerificationView.as_view(), name='otp-verification'),

    # Login Endpoints
    path('login/password/', PasswordLoginView.as_view(), name='password-login'),
    path('login/otp/', OTPLoginView.as_view(), name='otp-login'),
    path('login/verify-otp/', OTPLoginVerificationView.as_view(), name='otp-login-verification'),

    # Profile Endpoints
    path('profile/vendor/', VendorProfileView.as_view(), name='vendor-profile'),
    path('profile/customer/', CustomerProfileView.as_view(), name='customer-profile'),

    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('logout/', LogoutView.as_view(), name='logout'),


    path('addresses/', AddressListCreateView.as_view(), name='address-list-create'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token-verify'),

]
