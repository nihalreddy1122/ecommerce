from django.db import models
from django.contrib.auth import get_user_model
from vendors.models import VendorDetails
from django.utils.text import slugify
from PIL import Image
import os
from django.conf import settings

User = get_user_model()

# ================================
# Category Model
# ================================
from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    banners = models.ImageField(upload_to='category_banners/', blank=True, null=True, help_text="Banner image for the category")
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories'
    )
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True, help_text="Icon image for the category")

    class Meta:
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.parent.name if self.parent else 'Root'})"

    def get_leaf_categories(self):
        # Recursively fetch all leaf categories
        if not self.subcategories.exists():
            return [self]
        leaves = []
        for subcategory in self.subcategories.all():
            leaves.extend(subcategory.get_leaf_categories())
        return leaves

    def get_all_subcategories(self):
        """
        Recursively fetch all subcategories, including nested ones.
        """
        subcategories = set(self.subcategories.all())
        for subcategory in self.subcategories.all():
            subcategories.update(subcategory.get_all_subcategories())
        return subcategories

# ================================
# Attribute and Attribute Value Models
# ================================
class Attribute(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True, blank=True)

    class Meta:
        unique_together = ('attribute', 'value')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.value)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

# ================================
# Product Model
# ================================
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify

class Product(models.Model):
    vendor = models.ForeignKey(VendorDetails, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(blank=True, null=True, help_text="Detailed product description")
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    additional_details = models.JSONField(blank=True, null=True, help_text="Structured additional details for the product")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    thumbnail = models.ImageField(upload_to='product_thumbnails/',null=True)
    stock = models.PositiveIntegerField(default= 0)
    is_active = models.BooleanField(default=True)
    is_returnable = models.BooleanField(default=False, help_text="Can this product be returned?")
    max_return_days = models.PositiveIntegerField(blank=True, null=True, help_text="Maximum return days (if returnable)")
    is_cancelable = models.BooleanField(default=True, help_text="Can this product be canceled?")
    cancellation_stage = models.CharField(
        max_length=50,
        choices=[
            ('before_packing', 'Before Packing'),
            ('before_shipping', 'Before Shipping'),
            ('before_delivery', 'Before Delivery'),
        ],
        blank=True,
        null=True,
        help_text="Stage at which cancellation is allowed"
    )
    is_cod_allowed = models.BooleanField(default=True, help_text="Is cash on delivery allowed for this product?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Validate returnable logic
        if self.is_returnable and not self.max_return_days:
            raise ValidationError("Max return days must be specified if the product is returnable.")
        
        # Validate cancelable logic
        if self.is_cancelable and not self.cancellation_stage:
            raise ValidationError("Cancellation stage must be specified if the product is cancelable.")

    def save(self, *args, **kwargs):
        # Call clean method for validation before saving
        self.clean()
        
        if not self.slug:
            self.slug = slugify(f"{self.vendor.id}-{self.name}")

        if not self.sku:
            random_number = random.randint(1000, 9999)
            self.sku = slugify(f"{self.name[:3].upper()}-{self.vendor.shop_name[:3].upper()}-{random_number}")

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# ================================
# Product Variant Modell
# ================================
from django.db import models
from django.utils.text import slugify
from PIL import Image
import os
from django.conf import settings

import random
import string
from django.utils.text import slugify

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    attributes = models.ManyToManyField(AttributeValue, related_name='variants')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    offer_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    sku = models.CharField(max_length=14, unique=True, blank=True, help_text="Unique SKU for the product variant")

    @property
    def discount_percentage(self):
        if self.base_price > 0:
            return ((self.base_price - self.offer_price) / self.base_price) * 100
        return 0

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Check if the instance is being created
        super().save(*args, **kwargs)  # Save the instance to generate primary key

        if is_new and not self.sku:
            # Generate SKU in the format XXX-XXX-XXXX
            random_chars = ''.join(random.choices(string.ascii_uppercase, k=3))  # First 3 letters
            random_middle = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))  # Next 3
            random_digits = ''.join(random.choices(string.digits, k=4))  # Last 4 digits
            self.sku = f"{random_chars}-{random_middle}-{random_digits}"
            super().save(update_fields=['sku'])  # Update SKU field after creation

    def __str__(self):
        if not self.pk:
            return "Unsaved ProductVariant"
        attributes = ", ".join([str(value) for value in self.attributes.all()])
        return f"{self.product.name} ({attributes})"


class VariantImage(models.Model):
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='variant_images/')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._convert_image_to_jpeg()

    def _convert_image_to_jpeg(self):
        if self.image:
            try:
                input_path = self.image.path
                output_path = f"{os.path.splitext(input_path)[0]}.jpeg"
                if not os.path.exists(output_path):
                    with Image.open(input_path) as img:
                        img = img.convert('RGB')
                        img.save(output_path, 'JPEG', quality=85)
                    self.image.name = os.path.relpath(output_path, settings.MEDIA_ROOT)
                    super().save(update_fields=['image'])
            except Exception as e:
                print(f"Error converting image to JPEG: {e}")

    def __str__(self):
        return f"Image for Variant {self.product_variant.sku}"





# ================================
# Product Image Model
# ================================
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._convert_image_to_jpeg()

    def _convert_image_to_jpeg(self):
        if self.image:
            try:
                input_path = self.image.path
                output_path = f"{os.path.splitext(input_path)[0]}.jpeg"
                if not os.path.exists(output_path):
                    with Image.open(input_path) as img:
                        img = img.convert('RGB')
                        img.save(output_path, 'JPEG', quality=85)
                    self.image.name = os.path.relpath(output_path, settings.MEDIA_ROOT)
                    super().save(update_fields=['image'])
            except Exception as e:
                print(f"Error converting image to JPEG: {e}")

    def __str__(self):
        return f"Image for {self.product.name}"

# App: products/models.py

from django.db import models
from django.core.exceptions import ValidationError
from vendors.models import VendorDetails
from .models import Product

class FeaturedProduct(models.Model):
    vendor = models.ForeignKey(
        VendorDetails,
        on_delete=models.CASCADE,
        related_name='featured_products',
        help_text="Vendor owning the featured product"
    )
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='featured_status',
        help_text="The featured product"
    )
    added_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the product was marked as featured")

    def save(self, *args, **kwargs):
        # Enforce 10-product limit per vendor
        if self.vendor.featured_products.count() >= 10:
            raise ValidationError("A vendor can only have 10 featured products.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Featured Product: {self.product.name} by {self.vendor.shop_name}"





from django.db import models
from django.utils.timezone import now
from .models import Product
from vendors.models import VendorDetails

class LimitedEditionProduct(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="limited_edition",
        help_text="The product being marked as Limited Edition"
    )
    vendor = models.ForeignKey(
        VendorDetails,
        on_delete=models.CASCADE,
        help_text="Vendor who is setting the Limited Edition"
    )
    limited_stock = models.PositiveIntegerField(
        help_text="Stock allocated specifically for Limited Edition"
    )
    available_from = models.DateTimeField(
        help_text="Start date for Limited Edition availability",
        default=now
    )
    available_until = models.DateTimeField(
        help_text="End date for Limited Edition availability"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-available_from']
        constraints = [
            models.CheckConstraint(
                check=models.Q(available_from__lt=models.F('available_until')),
                name="valid_limited_edition_dates"
            )
        ]

    def __str__(self):
        return f"Limited Edition: {self.product.name} ({self.limited_stock} items)"
