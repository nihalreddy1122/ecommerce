import os
import django
import random
from faker import Faker
from django.utils.crypto import get_random_string
import requests
from django.core.files.base import ContentFile

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_platform.settings')
django.setup()

from products.models import Category

fake = Faker()

def fetch_unique_image():
    """Fetch a completely unique image for each category."""
    try:
        # Generate a truly unique image URL by appending a random string to the seed
        unique_seed = get_random_string(10)
        image_url = f"https://picsum.photos/seed/{unique_seed}/200"
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            return ContentFile(response.content, name=f"category_{unique_seed}.jpg")
    except requests.exceptions.RequestException:
        print("Failed to fetch a unique image.")
    return None

def create_categories():
    """Create a hierarchy of categories with unique slugs and images."""
    root_categories = {
        "MEN": {
            "Clothing": ["T-Shirts", "Shirts", "Jeans", "Trousers", "Shorts", "Jackets", "Activewear", "Blazers", "Ethnic Wear"],
            "Footwear": ["Casual Shoes", "Formal Shoes", "Sports Shoes", "Sandals", "Slippers"],
            "Grooming": ["Fragrances", "Hair Care", "Beard Care", "Shaving Kits"],
            "Accessories": ["Watches", "Wallets", "Belts", "Sunglasses", "Caps & Hats", "Socks"]
        },
        "WOMEN": {
            "Clothing": ["Tops & Tees", "Dresses", "Kurtis", "Sarees", "Jeans", "Skirts", "Activewear", "Ethnic Wear"],
            "Footwear": ["Heels", "Flats", "Sandals", "Casual Shoes", "Sports Shoes"],
            "Beauty": ["Makeup", "Skin Care", "Hair Care", "Fragrances"],
            "Accessories": ["Jewelry", "Watches", "Sunglasses", "Handbags", "Clutches", "Belts"]
        },
        "KIDS": {
            "Clothing": ["Boys Clothing", "Girls Clothing", "Baby Clothing"],
            "Footwear": ["Sports Shoes", "Casual Shoes", "Sandals", "Baby Shoes"],
            "Toys": ["Action Figures", "Educational Toys", "Dolls & Dollhouses", "Puzzles"],
            "Accessories": ["Backpacks", "Watches", "Caps & Hats", "Socks"]
        },
        "ACCESSORIES": {
            "Men's Accessories": ["Watches", "Wallets", "Belts", "Sunglasses", "Caps & Hats", "Ties"],
            "Women's Accessories": ["Jewelry", "Handbags", "Clutches", "Watches", "Scarves & Stoles", "Sunglasses"],
            "Kids' Accessories": ["Backpacks", "Hats", "Hair Accessories", "Watches", "Socks"]
        }
    }

    for root, subcategories in root_categories.items():
        # Create root category
        root_category, created = Category.objects.get_or_create(
            name=root,
            defaults={
                "slug": f"{root.lower().replace(' ', '-')}-{get_random_string(4)}",
                "icon": fetch_unique_image(),
            }
        )

        if created:
            print(f"Created root category: {root}")

        # Create subcategories and sub-subcategories
        for sub_name, leaf_names in subcategories.items():
            sub_category, created = Category.objects.get_or_create(
                name=sub_name,
                parent=root_category,
                defaults={
                    "slug": f"{sub_name.lower().replace(' ', '-')}-{get_random_string(4)}",
                    "icon": fetch_unique_image(),
                }
            )

            if created:
                print(f"Created subcategory: {sub_name} under {root}")

            for leaf_name in leaf_names:
                leaf_category, created = Category.objects.get_or_create(
                    name=leaf_name,
                    parent=sub_category,
                    defaults={
                        "slug": f"{leaf_name.lower().replace(' ', '-')}-{get_random_string(4)}",
                        "icon": fetch_unique_image(),
                    }
                )

                if created:
                    print(f"Created leaf category: {leaf_name} under {sub_name}")

    print("Category hierarchy creation complete.")

# Run the script
if __name__ == "__main__":
    create_categories()
