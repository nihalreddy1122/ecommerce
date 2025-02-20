from django.urls import path
from .views import *
from customer.views import RefundDetailView

urlpatterns = [
    # Admin Logs
    path('logs/', AdminLogView.as_view(), name='admin-logs'),
    
    #Vendor Approvals
    path('vendor-approved/<int:id>/', VendorProfileUpdateView.as_view(), name='vendor-profile-update'),
    path('vendor-profile/<int:id>/', VendorProfileDetailView.as_view(), name='vendor-profile-detail'),

    # Vendor Payouts
    path('payouts/', VendorPayoutView.as_view(), name='vendor-payouts'),
    path('payouts/<int:payout_id>/', VendorPayoutView.as_view(), name='vendor-payout-detail'),

    # Refunds
    path('refunds/<int:refund_id>/', RefundDetailView.as_view(), name='refund-detail'),
    path('refunds/<int:refund_id>/<str:action>/', RefundActionView.as_view(), name='refund-action'),


    # orders places
    path('orders/placed/', ListPlacedOrdersView.as_view(), name='list-placed-orders'),

    #address by user

    path('soft-data/', CreateSoftDataView.as_view(), name='create-soft-data'),

    # xpressbee 
    path('xpressbee/login/', XpressBeeLogin.as_view(), name = 'xpress-bee-login'),
]
