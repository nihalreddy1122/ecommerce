from django.db import models
from products.models import Category
from vendors.models import VendorDetails

class BannerType(models.TextChoices):
    HERO = 'hero', 'Hero'
    GRID = 'grid', 'Grid'
    SCROLL = 'scroll', 'scroll'

class Banner(models.Model):
    title = models.CharField(max_length=255, help_text="Title of the banner")
    description = models.TextField(blank=True, null=True, help_text="Optional description for the banner")
    image = models.ImageField(upload_to='banners/',null=True , help_text="Image for the banner")
    banner_type = models.CharField(
        max_length=10,
        choices=BannerType.choices,
        default=BannerType.HERO,
        help_text="Type of the banner (Hero, Grid, scrollbar)"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=True, null=True,
        help_text="Optional category linked to this banner"
    )
    store = models.ForeignKey(
        VendorDetails, on_delete=models.CASCADE, blank=True, null=True,
        help_text="Optional store linked to this banner"
    )
    external_url = models.URLField(blank=True, null=True, help_text="Custom external URL for the banner")
    position = models.CharField(
        max_length=20,
        choices=[('top', 'Top'), ('middle', 'Middle'), ('scroll', 'Scroll')],
        default='top',
        help_text="Position of the banner on the page"
    )
    priority = models.PositiveIntegerField(default=0, help_text="Display priority for ordering banners")
    is_active = models.BooleanField(default=True, help_text="Indicates if the banner is active")
    created_at = models.DateTimeField(auto_now_add=True, help_text="When the banner was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="When the banner was last updated")

    class Meta:
        ordering = ['-priority', 'created_at']  # Higher priority banners appear first

    def __str__(self):
        return f"{self.title} ({self.banner_type})"
