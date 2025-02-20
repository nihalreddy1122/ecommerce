import os
import django
import random
import string
from faker import Faker
from django.utils.crypto import get_random_string

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from vendors.models import VendorDetails

User = get_user_model()
fake = Faker()

def create_clothing_brand_vendors(count=5):
    clothing_brands = [
        "StyleHub",
        "UrbanVogue",
        "TrendThreads",
        "Chic Couture",
        "Fashionista Co.",
        "Elite Apparel",
        "Modern Wardrobe",
        "ClassyClad",
        "Wardrobe Essentials",
        "RunwayReady"
    ]

    for i in range(count):
        # Generate realistic random user details
        email = f"{clothing_brands[i].replace(' ', '').lower()}@example.com"
        password = "SecurePassword123"
        first_name = fake.first_name()
        last_name = fake.last_name()
        phone_number = fake.phone_number().replace(" ", "")[:10]  # Ensure 10 digits

        # Create User object
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            user_type="vendor",
        )

        # Generate random vendor details
        shop_name = clothing_brands[i]
        shop_address = fake.address()
        bank_account_number = ''.join(random.choices(string.digits, k=12))
        bank_name = fake.company()
        ifsc_code = f"IFSC{get_random_string(6).upper()}"
        state = fake.state()
        city = fake.city()
        pincode = fake.postcode()

        # Create VendorDetails object
        VendorDetails.objects.create(
            user=user,
            shop_name=shop_name,
            address=shop_address,
            bank_account_number=bank_account_number,
            bank_name=bank_name,
            ifsc_code=ifsc_code,
            state=state,
            city=city,
            pincode=pincode,
            is_verified=False,
            shop_logo=None,  # No shop logo assigned
        )

    print(f"Successfully created {count} clothing brand vendors.")

# Call the function
if __name__ == "__main__":
    create_clothing_brand_vendors()
