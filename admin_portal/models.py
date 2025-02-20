from django.db import models
from django.conf import settings
from cart_orders.models import Order, OrderItem
from vendors.models import VendorDetails
import os 

# Model to log admin activities
class AdminLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                             help_text="Admin who performed the action")
    action = models.CharField(max_length=255, help_text="Description of the action performed")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="When the action was performed")

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"


# Model to track payouts to vendors
class VendorPayout(models.Model):
    vendor = models.ForeignKey(VendorDetails, on_delete=models.CASCADE, related_name="payouts",
                               help_text="Vendor receiving the payout")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Payout amount")
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('processed', 'Processed')],
        default='pending',
        help_text="Status of the payout"
    )
    processed_at = models.DateTimeField(null=True, blank=True, help_text="When the payout was processed")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the payout was created")

    def __str__(self):
        return f"Payout for {self.vendor.user.email} - {self.amount} - {self.status}"


from django.conf import settings
from cart_orders.models import OrderItem

def refund_media_upload_path(instance, filename):
    """
    Define the upload path for refund media files dynamically.
    """
    return os.path.join(
        "orders", 
        f"{instance.refund.order_item.order.id}", 
        f"refunds/{instance.id}/", 
        filename
    )

class Refund(models.Model):
    REFUND_STATUS_CHOICES = [
        ('initiated', 'Refund Initiated'),
        ('processed', 'Refund Processed'),
        ('rejected', 'Refund Rejected'),
        ('implemented', 'Refund Implemented'),
    ]

    order_item = models.ForeignKey(
        OrderItem, 
        on_delete=models.CASCADE, 
        related_name="refunds", 
        help_text="The order item for which the refund is requested."
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Refund amount for the order item."
    )
    status = models.CharField(
        max_length=20,
        choices=REFUND_STATUS_CHOICES,
        default='initiated',
        help_text="Current status of the refund."
    )
    reason = models.TextField(
        default = "__________",
        help_text="Reason provided by the customer for the refund."
    )
    refund_initiated_date = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="The date when the refund was initiated."
    )
    refund_processed_date = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="The date when the refund was processed."
    )
    refund_rejected_date = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="The date when the refund was rejected."
    )
    refund_implemented_date = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="The date when the refund was implemented."
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        help_text="The date when the refund was created."
    )

    def __str__(self):
        return f"Refund for {self.order_item.id} - {self.status}"


class RefundMedia(models.Model):
    refund = models.ForeignKey(
        Refund, 
        on_delete=models.CASCADE, 
        related_name="media", 
        help_text="The refund associated with this media"
    )
    media = models.FileField(
        upload_to=refund_media_upload_path, 
        help_text="Image or video file supporting the refund request"
    )

    def save(self, *args, **kwargs):
        """
        Override save to perform media processing if required.
        """
        super().save(*args, **kwargs)
        if self.media and self.media.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            self._convert_image_to_jpeg()

    def _convert_image_to_jpeg(self):
        """
        Convert image to JPEG format for consistency.
        """
        try:
            from PIL import Image
            input_path = self.media.path
            output_path = f"{os.path.splitext(input_path)[0]}.jpeg"
            if not os.path.exists(output_path):
                with Image.open(input_path) as img:
                    img = img.convert('RGB')
                    img.save(output_path, 'JPEG', quality=85)
                self.media.name = os.path.relpath(output_path, settings.MEDIA_ROOT)
                super().save(update_fields=['media'])
        except Exception as e:
            print(f"Error converting image to JPEG: {e}")

    def __str__(self):
        return f"Media for Refund {self.refund.id}"
    
class SoftData(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="soft_data")
    pickup_address = models.TextField(help_text="Pickup address provided by admin")
    shipping_address = models.TextField(help_text="Fetched from the order")
    tracking_id = models.CharField(max_length=100, blank=True, null=True, help_text="Tracking ID from Delhivery")
    payment_status = models.CharField(
        max_length=20,
        choices=[("unpaid", "Unpaid"), ("paid", "Paid")],
        default="unpaid",
        help_text="Payment status for the order"
    )
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Weight of the order in kilograms"
    )
    dimensions = models.JSONField(
        help_text="Dimensions of the order (length, breadth, height) in cm"
    )
    serviceability_checked = models.BooleanField(default=False, help_text="Indicates if serviceability check is done")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
