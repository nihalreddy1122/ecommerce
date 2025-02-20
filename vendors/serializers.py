from rest_framework import serializers
from .models import VendorDetails, StoreImage
from django.core.exceptions import ValidationError
from cart_orders.models import OrderItem
from authusers.serializers import AddressSerializer

class StoreImageSerializer(serializers.ModelSerializer):
    """
    Serializer for the StoreImage model.
    """
    class Meta:
        model = StoreImage
        fields = ['id', 'image', 'created_at']

class VendorDetailsSerializer(serializers.ModelSerializer):
    store_images = StoreImageSerializer(many=True, read_only=True)

    class Meta:
        model = VendorDetails
        fields = [
            'shop_name',
            'shop_logo',
            'store_images',
            'bio',
            'video',
            'city',
            'state',
            'address',
            'pincode',
            'bank_account_number',
            'bank_name',
            'ifsc_code',
            'id_proof_type',
            'id_proof_file',
            'is_verified',
        ]
        read_only_fields = ['is_verified']

    def validate_video(self, value):
        """Validate the uploaded video for size and duration."""
        if value.size > 50 * 1024 * 1024:  # 50MB limit
            raise ValidationError("Video size cannot exceed 50MB.")
        return value

    def validate_bank_account_number(self, value):
        """Ensure the bank account number is numeric."""
        if not value.isdigit():
            raise ValidationError("Bank account number must be numeric.")
        return value

    def validate(self, data):
        """Custom validation to ensure all required fields are filled."""
        required_fields = [
            'shop_name',
            'bio',
            'bank_account_number',
            'bank_name',
            'ifsc_code',
            'id_proof_type',
            'city',
            'state',
            'address',
            'pincode',
        ]
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f"{field} is required.")
        return data



class SimplifiedVendorSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorDetails
        fields = ['id','shop_name', 'city', 'state', 'address', 'pincode']




from products.serializers import ProductVariantSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    delivery_address = serializers.SerializerMethodField()  # Add delivery address field
    customer_details = serializers.SerializerMethodField()  # Add customer details field
    variant_image = serializers.SerializerMethodField()  # Add this field
    
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'customer_details',  
            'order',
            'product_variant',
            'quantity',
            'price',
            'created_at',
            'updated_at',
            'payment_status',
            'delivery_address', 
            'variant_image',  # Include the variant image in the response
 
        ]

    def get_delivery_address(self, obj):
        """
        Retrieve the delivery address from the related order's DeliveryDetail.
        """
        if hasattr(obj.order, 'delivery_detail') and obj.order.delivery_detail:
            return AddressSerializer(obj.order.delivery_detail.address).data
        return None  # Return None if no delivery detail is associated

    def get_customer_details(self, obj):
        """
        Retrieve customer details from the related order.
        """
        customer = obj.order.customer
        return {
            "name": f"{customer.first_name} {customer.last_name}".strip(),
            "email": customer.email,
            "phone_number": customer.phone_number,  # Assuming the User model includes phone_number
        }

    def get_variant_image(self, obj):
        """
        Fetch the first image for the product variant.
        """
        if obj.product_variant.images.exists():
            return obj.product_variant.images.first().image.url  # Adjust field if necessary
        return None



class VendorDashboardSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    total_earnings_week = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_earnings_day = serializers.DecimalField(max_digits=10, decimal_places=2)


from rest_framework import serializers
from .models import VendorDetails

class VendorShopSerializer(serializers.ModelSerializer):
    store_images = StoreImageSerializer(many=True, read_only=True)

    class Meta:
        model = VendorDetails
        fields = ['id', 'bio', 'shop_name', 'shop_logo','store_images']  # Added stored_images

