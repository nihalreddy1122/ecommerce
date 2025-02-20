from django.db import models
from cart_orders.models import *
from products.models import *
from authusers.models import *

# Create your models here.

from django.core.validators import MinValueValidator, MaxValueValidator

def review_media_upload_path(instance, filename):
    """
    Define the upload path for media files dynamically.
    """
    directory = f"reviews/{instance.review.id}/media/"
    return os.path.join(directory, filename)


class Review(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    review_text = models.TextField(blank=True, null=True)
    rating = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Rating should be between 0 and 5."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.customer.email} for {self.product.name}"


class ReviewMedia(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='media',
        help_text="The review associated with this media"
    )
    media = models.FileField(
        upload_to=review_media_upload_path,
        help_text="Image or video file associated with the review"
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
        return f"Media for Review {self.review.id}"




from django.db import models
from django.conf import settings
from products.models import Product

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"

from django.db.models import Avg
class OverallReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='overall_review')
    average_rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    
    def update_average_rating(self):
        self.average_rating = Review.objects.filter(product=self.product).aggregate(Avg('rating'))['rating__avg'] or 0
        self.save()