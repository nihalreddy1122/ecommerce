from celery import shared_task
from PIL import Image
import os
from django.conf import settings
from django.core.cache import cache
from .models import ProductImage, Category


@shared_task
def convert_image_to_jpeg(image_path):
    """
    Convert an image to JPEG format if not already in JPEG format.
    """
    try:
        output_path = f"{os.path.splitext(image_path)[0]}.jpeg"
        if not os.path.exists(output_path):  # Avoid overwriting existing files
            with Image.open(image_path) as img:
                img = img.convert('RGB')  # Ensure the image is in RGB mode
                img.save(output_path, 'JPEG', quality=85)
            return f"Converted {image_path} to {output_path}"
        return f"Image {output_path} already exists."
    except Exception as e:
        return f"Error processing {image_path}: {e}"


@shared_task
def refresh_category_cache():
    """
    Refresh the cached category structure and associated products.
    """
    categories = Category.objects.all()
    results = []

    for category in categories:
        # Cache key for products under this category
        cache_key = f"category_products_{category.slug}"
        products = category.products.all()  # Assuming related_name='products' in Category
        product_data = [
            {"id": product.id, "name": product.name, "price": product.base_price}
            for product in products
        ]
        cache.set(cache_key, product_data, timeout=6 * 60 * 60)  # Cache for 6 hours
        results.append(f"Cached products for category {category.slug}")

    return results


@shared_task
def process_all_images():
    """
    Convert all ProductImage files to JPEG.
    """
    images = ProductImage.objects.all()
    results = []

    for image in images:
        image_path = image.image.path
        result = convert_image_to_jpeg(image_path)
        results.append(result)

    return results


@shared_task
def refresh_category_hierarchy_cache():
    """
    Cache the entire category hierarchy for optimized front-end loading.
    """
    category_data = list(
        Category.objects.all().values("id", "name", "slug", "parent_id")
    )
    cache.set("category_hierarchy", category_data, timeout=6 * 60 * 60)  # Cache for 6 hours
    return "Category hierarchy cached successfully."
