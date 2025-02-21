from django.urls import path
from .views import *
urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('checkout/<int:order_id>/', CheckoutView.as_view(), name='checkout-detail'),
    path('deliverydetails/', DeliveryDetailView.as_view(), name = 'delivery-detail'),
    path('deliverydetails/<int:pk>/', DeliveryDetailView.as_view(), name='delivery-detail-specific'),
    path('buynow/', BuyNowView.as_view(), name='Buy-Now'),
    path('payment/init/', PaymentInitializationView.as_view(), name= 'payment-init'),   # razor pay payment initialization
    path('retry-payment/', RetryPaymentView.as_view(), name='retry-payment'),
    path('payment/verify/', PaymentVerificationView.as_view(), name= "payment-verify"),
    path('orders/<int:order_id>/items/', OrderItemListView.as_view(), name='order-item-list'),
    # address by user

    #path('address/',UserAddressListView.as_view(), name='generate_address'),

#_______________________________________CUSTOMER________________________________________________________________

    path('generate-shipping-label/<int:order_item_id>/', generate_shipping_label, name='generate_shipping_label'),
    path('payment/webhook/', RazorpayWebhookView.as_view(), name='razorpay-webhook'),


]
