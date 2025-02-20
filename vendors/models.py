from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from authusers.models import User
from PIL import Image  # For image resizing
import logging

import os

User = get_user_model()

# Helper function for file upload path
def upload_to(instance, filename):
    return f"vendor_images/{instance.user.id}/{filename}"

logger = logging.getLogger(__name__)  # Initialize the logger

class VendorDetails(models.Model):
    ID_PROOF_CHOICES = [
        ('aadhar', 'Aadhar Card'),
        ('dl', 'Driving License'),
        ('pan', 'PAN Card'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_details')
    shop_name = models.CharField(max_length=255, blank=True, null=True)
    shop_logo = models.ImageField(upload_to="vendor_images/", blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    video = models.FileField(upload_to='vendor_videos/', blank=True, null=True)
    bank_account_number = models.CharField(max_length=20, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    id_proof_type = models.CharField(max_length=20, choices=ID_PROOF_CHOICES, blank=True, null=True)
    id_proof_file = models.FileField(upload_to='vendor_id_proofs/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    address = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True) 
    pincode = models.CharField(max_length=6, blank=True, null=True) 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Save the model first to ensure the file exists in the filesystem
        super().save(*args, **kwargs)
        # Convert image to JPEG if shop_logo exists
        if self.shop_logo:
            self._convert_image_to_jpeg()

    def _convert_image_to_jpeg(self):
        try:
            input_path = self.shop_logo.path  # Path to the original file
            logger.info(f"Converting image at path: {input_path}")
            base = os.path.splitext(input_path)[0]  # Get base file path without extension
            jpeg_path = f"{base}.jpeg"
            logger.info(f"JPEG path: {jpeg_path}")

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(jpeg_path), exist_ok=True)

            # Convert and save as JPEG
            with Image.open(input_path) as image:
                image = image.convert("RGB")  # Convert to RGB if not already
                image.save(jpeg_path, format="JPEG", quality=85)
                logger.info(f"Image converted and saved to JPEG at: {jpeg_path}")

            # Update shop_logo path to JPEG without triggering save
            self.shop_logo.name = os.path.relpath(jpeg_path, settings.MEDIA_ROOT)
            super().save(update_fields=["shop_logo"])  # Save only the updated field
            logger.info(f"shop_logo updated to: {self.shop_logo.name}")
        except Exception as e:
            logger.error(f"Error converting image to JPEG: {e}")


    def __str__(self):
        return f"Vendor Details for {self.user.email}"

class StoreImage(models.Model):
    vendor = models.ForeignKey(
        VendorDetails, on_delete=models.CASCADE, related_name='store_images'
    )
    image = models.ImageField(upload_to='store_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Store Image for Vendor: {self.vendor.shop_name}"



from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VendorDetails
from .tasks import send_vendor_activation_email_task

@receiver(post_save, sender=VendorDetails)
def send_vendor_activation_email(sender, instance, created, **kwargs):
    if instance.is_verified:  # Only send email if the account is verified
        send_vendor_activation_email_task.delay(
            user_email=instance.user.email,
            user_first_name=instance.user.first_name,
        )





