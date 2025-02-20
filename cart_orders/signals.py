from django.db.models.signals import post_save
from django.dispatch import receiver
from cart_orders.models import OrderItem
from cart_orders.tasks import send_order_status_email_task

@receiver(post_save, sender=OrderItem)
def notify_status_change(sender, instance, **kwargs):
    """
    Trigger email notification when the order status changes.
    """
    if instance.order_status:  # Ensure the order status exists
        send_order_status_email_task.delay(instance.id)
