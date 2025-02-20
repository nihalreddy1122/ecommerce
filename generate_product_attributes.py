import os
import django
from django.utils.crypto import get_random_string

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_platform.settings')
django.setup()

from products.models import Attribute, AttributeValue

def create_attributes():
    """Create attributes and their respective values."""

    # Define attributes and their values based on categories
    attributes = {
        "FIT": ["Slim Fit", "Regular Fit", "Loose Fit"],
        "SIZE": ["XS", "S", "M", "L", "XL", "XXL"],
        "COLOR": ["Red", "Blue", "Green", "Black", "White", "Pink", "Beige"],
        "FABRIC": ["Cotton", "Polyester", "Linen", "Denim", "Silk", "Satin"],
        "MATERIAL": ["Leather", "Synthetic", "Canvas", "Suede", "Plastic"],
        "HEEL TYPE": ["Flat", "Stiletto", "Block", "Wedge"],
        "STYLE": ["Casual", "Formal", "Ethnic", "Sporty", "Party Wear"],
        "OCCASION": ["Daily Wear", "Party", "Office", "Outdoor"],
        "FRAGRANCE TYPE": ["Woody", "Citrus", "Floral", "Oriental", "Fresh"],
        "SKIN TYPE": ["Oily", "Dry", "Combination", "Normal"],
        "HAIR TYPE": ["Straight", "Wavy", "Curly", "Oily"],
        "AGE GROUP": ["Kids", "Teen", "Adult", "Senior"],
        "BRAND": ["Nike", "Adidas", "Puma", "Reebok", "Levi's", "H&M"],
        "LENS TYPE": ["UV Protected", "Polarized", "Photochromic"],
    }

    for attribute_name, values in attributes.items():
        # Create the attribute
        attribute, created = Attribute.objects.get_or_create(
            name=attribute_name,
            defaults={"slug": attribute_name.lower().replace(" ", "-")}
        )
        if created:
            print(f"Created attribute: {attribute_name}")

        # Create attribute values
        for value in values:
            value_slug = f"{value.lower().replace(' ', '-')}-{get_random_string(4)}"
            attribute_value, value_created = AttributeValue.objects.get_or_create(
                attribute=attribute,
                value=value,
                defaults={"slug": value_slug}
            )
            if value_created:
                print(f"  - Created value: {value} for attribute: {attribute_name}")

    print("Attribute creation process completed.")

# Run the script
if __name__ == "__main__":
    create_attributes()
