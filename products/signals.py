from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProductImage

@receiver(post_save, sender=ProductImage)
def convert_image_on_save(sender, instance, created, **kwargs):
    """
    Signal to convert an uploaded ProductImage to JPEG format after it's saved.
    """
    if created and instance.image:  # Only process if the instance is newly created and has an image
        try:
            instance.convert_image_to_jpeg()  # Assuming `convert_image_to_jpeg` is now a public method
        except Exception as e:
            print(f"Error converting image to JPEG: {e}")
