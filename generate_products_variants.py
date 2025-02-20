import os
import django
import random
from faker import Faker
from django.utils.crypto import get_random_string
from django.core.files.base import ContentFile
import requests
from PIL import Image
from io import BytesIO

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_platform.settings')
django.setup()

from products.models import Product, ProductVariant, AttributeValue, ProductImage, VariantImage
from vendors.models import VendorDetails
from products.models import Category

fake = Faker()

CATEGORY_PRODUCTS = {
    "T-Shirts": [
        ("Graphic Tee", "A trendy graphic T-shirt made of 100% cotton for everyday wear."),
        ("Plain Cotton Tee", "A plain T-shirt made of high-quality cotton for comfort."),
        ("Polo Shirt", "A classic polo shirt with a stylish collar."),
        ("V-Neck Tee", "A soft V-neck T-shirt perfect for casual outings."),
    ],
    "Shirts": [
        ("Formal Shirt", "A crisp formal shirt ideal for office or events."),
        ("Casual Check Shirt", "A comfortable checkered shirt for casual wear."),
        ("Linen Shirt", "A breathable linen shirt for summer days."),
        ("Denim Shirt", "A rugged denim shirt for a bold look."),
    ],
    "Jeans": [
        ("Skinny Jeans", "Slim-fit jeans for a modern and stylish appearance."),
        ("Regular Fit Jeans", "Classic regular-fit jeans for daily wear."),
        ("Stretch Jeans", "Comfortable stretch jeans for flexibility."),
        ("Ripped Jeans", "Edgy ripped jeans for a trendy style."),
    ],
}

def fetch_image(category_name):
    """Fetch an image and ensure it is converted to JPEG if necessary."""
    try:
        response = requests.get(f"https://picsum.photos/300/300?random={random.randint(1, 1000)}", stream=True)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image = image.convert("RGB")  # Ensure compatibility with JPEG
            img_io = BytesIO()
            image.save(img_io, format="JPEG")
            return ContentFile(img_io.getvalue(), name=f"{category_name}_{get_random_string(5)}.jpg")
    except Exception as e:
        print(f"Failed to fetch or process image: {e}")
    return None

def get_product_name_and_description(category_name):
    """Get a relevant product name and description based on the category."""
    for key, products in CATEGORY_PRODUCTS.items():
        if key.lower() in category_name.lower():
            return random.choice(products)
    return (f"Generic {category_name}", f"Description for {category_name}")

def create_products():
    vendors = VendorDetails.objects.all()
    products_per_vendor = 10
    variants_per_product = 3
    images_per_variant = 3

    for vendor in vendors:
        for _ in range(products_per_vendor):
            category = random.choice(Category.objects.all())
            category_name = category.name

            product_name, product_description = get_product_name_and_description(category_name)

            is_returnable = random.choice([True, False])
            max_return_days = random.randint(5, 30) if is_returnable else None

            thumbnail_image = fetch_image(category_name)

            product = Product.objects.create(
                vendor=vendor,
                name=product_name,
                slug=f"{product_name.lower().replace(' ', '-')}-{get_random_string(4)}",
                description=product_description,
                category=category,
                thumbnail=thumbnail_image,
                stock=random.randint(50, 200),
                is_active=True,
                is_returnable=is_returnable,
                max_return_days=max_return_days,
                is_cancelable=random.choice([True, False]),
                cancellation_stage=random.choice(["before_packing", "before_shipping", "before_delivery"]),
                is_cod_allowed=random.choice([True, False]),
            )

            for _ in range(3):
                product_image = fetch_image(category_name)
                if product_image:
                    ProductImage.objects.create(product=product, image=product_image)

            for _ in range(variants_per_product):
                base_price = round(random.uniform(500.00, 2000.00), 2)
                offer_price = round(random.uniform(100.00, base_price - 1), 2)

                variant = ProductVariant.objects.create(
                    product=product,
                    base_price=base_price,
                    offer_price=offer_price,
                    stock=random.randint(10, 100),
                )

                attributes = AttributeValue.objects.order_by('?')[:2]
                variant.attributes.set(attributes)

                for _ in range(images_per_variant):
                    variant_image = fetch_image(category_name)
                    if variant_image:
                        VariantImage.objects.create(product_variant=variant, image=variant_image)

        print(f"Created {products_per_vendor} products for vendor: {vendor.user.email}")

    print("Product creation completed successfully.")

# Run the script
if __name__ == "__main__":
    create_products()
