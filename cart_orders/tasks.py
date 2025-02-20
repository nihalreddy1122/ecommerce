from django.db import models  # Add this import
from celery import shared_task  # Add this import for the shared_task decorator
from django.conf import settings  # Import settings to use BASE_URL
from django.utils.timezone import now, timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Cart, Order  # Import specific models used
from ecommerce_platform.settings import EMAIL_HOST_USER

from django.shortcuts import get_object_or_404

def update_payment_status(order_id):
    order = get_object_or_404(Order, id=order_id)  # Correct model reference
    for item in order.items.all():  # Use `.all()` to retrieve related items
        item.payment_status = "paid"  # Corrected typo
        item.save()

@shared_task
def send_packed_email(order_id):
    """
    Celery task to send email notifications when an order is packed.
    """
    try:
        order = Order.objects.get(id=order_id)

        # Send email to customer
        customer_email_body = render_to_string(
            'emails/order_packed_customer.html',
            {
                'customer_name': order.customer.get_full_name(),
                'order_id': order.id,
                'year': now().year,
            }
        )
        send_mail(
            subject="Your order has been packed!",
            message="",
            from_email=EMAIL_HOST_USER,
            recipient_list=[order.customer.email],
            fail_silently=False,
            html_message=customer_email_body,
        )

        # Send email to admin
        admin_email_body = render_to_string(
            'emails/order_packed_admin.html',
            {
                'vendor_name': order.vendor.user.get_full_name(),
                'order_id': order.id,
                'year': now().year,
            }
        )
        send_mail(
            subject=f"Vendor packed order #{order.id}",
            message="",
            from_email=EMAIL_HOST_USER,
            recipient_list=["rerddyrebba72@gmail.com"],  # Admin email
            fail_silently=False,
            html_message=admin_email_body,
        )

        return f"Emails sent for order {order_id}"

    except Order.DoesNotExist:
        return f"Order {order_id} does not exist"

def send_email(subject, message, recipient):
    """
    Utility function to send emails.
    """
    send_mail(
        subject=subject,
        message=message,
        from_email=EMAIL_HOST_USER,
        recipient_list=[recipient],
        fail_silently=False,
    )















from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from cart_orders.models import Order
from django.conf import settings

@shared_task
def send_order_placed_email(order_id):
    """
    Send an order confirmation email to the customer after successful payment.
    """
    try:
        order = Order.objects.get(id=order_id)
        subject = f"Order #{order.id} Confirmed!"
        recipient = order.customer.email

        # Render email content
        email_body = render_to_string('emails/order_placed.html', {
            'order': order,
            'customer': order.customer,
            'items': order.items.all(),
            'total_price': order.total_price,
        })

        # Send the email
        send_mail(
            subject=subject,
            message="",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recipient],
            html_message=email_body,
        )
    except Order.DoesNotExist:
        print(f"Order with ID {order_id} does not exist.")




from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from cart_orders.models import OrderItem
from django.conf import settings

@shared_task
def send_order_status_email_task(order_item_id):
    """
    Send an email notification to the customer when the order status changes.
    """
    try:
        order_item = OrderItem.objects.get(id=order_item_id)
        customer_email = order_item.order.customer.email

        subject = f"Order #{order_item.order.id} Status Update"
        message = f"Your order item {order_item.product_variant.product.name} status has been updated to {order_item.order_status}."
        
        # Construct the customer's name
        customer_name = f"{order_item.order.customer.first_name} {order_item.order.customer.last_name}".strip()
        
        # Use an email template for better formatting
        html_message = render_to_string(
            'emails/order_status_update.html',
            {
                'order_item': order_item,
                'customer_name': customer_name,
                'status': order_item.order_status,
            }
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[customer_email],
            fail_silently=False,
            html_message=html_message,
        )
    except OrderItem.DoesNotExist:
        print(f"OrderItem with ID {order_item_id} does not exist.")
    except Exception as e:
        print(f"An error occurred while sending the order status email: {str(e)}")






@shared_task
def delete_stale_orders():
    """
    Deletes orders that remain in 'pending' or 'failed' payment status for more than 5 minutes,
    excluding COD orders (cod_pending).
    """
    from django.utils.timezone import now
    from datetime import timedelta
    from cart_orders.models import Order

    threshold_time = now() - timedelta(minutes=1)  # Orders older than 5 minutes
    stale_orders = Order.objects.filter(
        payment_status__in=['pending', 'failed'],  # Exclude COD
        created_at__lt=threshold_time
    ).exclude(payment_status='cod_pending')  # Explicitly exclude COD orders

    # Log orders being deleted for debugging
    for order in stale_orders:
        print(f"Deleting stale order: {order.id} - {order.payment_status}")

    # Delete stale orders
    stale_orders.delete()

