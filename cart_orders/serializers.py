from rest_framework import serializers
from .models import *
from products.serializers import ProductVariantSerializer
from vendors.serializers import SimplifiedVendorSerializer
from authusers.serializers import AddressSerializer

# ================================
# Cart Serializers
# ================================
class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for individual cart items.
    Includes product details and calculates the subtotal for the item.
    """
    product_variant = ProductVariantSerializer(read_only=True)
    product_variant_id = serializers.PrimaryKeyRelatedField(
        queryset=CartItem.objects.all(),
        source='product_variant',
        write_only=True,
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product_variant', 'product_variant_id', 'quantity', 'subtotal']

    def get_subtotal(self, obj):
        return obj.get_subtotal()


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for the cart.
    Includes nested cart items and calculates the total price of the cart.
    """
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price']

    def get_total_price(self, obj):
        return sum(item.get_subtotal() for item in obj.items.all())


# ================================
# Order Serializers
# ================================
from authusers.serializers import UserSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for individual order items.
    Includes product variant details and order status.
    """
    product_variant = ProductVariantSerializer(read_only=True)
    variant_image = serializers.SerializerMethodField()
    product_variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),  # Fixed queryset to use ProductVariant
        source="product_variant",
        write_only=True,
    )
    customer = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 
            'customer', 
            'product_variant', 
            'product_variant_id', 
            'quantity', 
            'price', 
            'order_status',  # Added the order_status field
            'created_at', 
            'updated_at',
            'variant_image',  # Include this field for the image
        ]
        read_only_fields = ['id', 'order_status', 'created_at', 'updated_at']  # Made order_status read-only

    def get_customer(self, obj):
        """
        Fetch customer details from the related order.
        """
        user = obj.order.customer
        return UserSerializer(user).data
    def get_variant_image(self, obj):
        """
        Retrieve the first image for the specific product variant.
        """
        if obj.product_variant.images.exists():
            return obj.product_variant.images.first().image.url  # Fetch the first image's URL
        return None  # Return None if no image exists

class SubOrderSerializer(serializers.ModelSerializer):
    """
    Serializer for vendor-specific sub-orders.
    Includes simplified vendor details and items.
    """
    vendor = SimplifiedVendorSerializer(read_only=True)
    items = serializers.SerializerMethodField()

    class Meta:
        model = SubOrder
        fields = ['id', 'vendor', 'subtotal', 'items']

    def get_items(self, obj):
        # Get all items in the sub-order
        order_items = obj.order.items.filter(product_variant__product__vendor=obj.vendor)
        print("Order Items:", order_items)  # Check the fetched items
        return OrderItemSerializer(order_items, many=True).data


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the main order.
    Includes all items and sub-orders.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    sub_orders = SubOrderSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True)  # Include address details

    class Meta:
        model = Order
        fields = ['id', 'customer', 'total_price', 'payment_status', 'created_at', 'updated_at', 'items', 'sub_orders', 'address','created_at', 'updated_at',] # Include created_at

        read_only_fields = ['customer', 'total_price', 'payment_status', 'created_at', 'updated_at']




class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'full_name', 'phone_number', 'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country']

from authusers.serializers import AddressSerializer

class DeliveryDetailSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)  # Nested serializer to include full address details
    address_details = serializers.JSONField(write_only=True, required=False)  # Write-only for dynamic address creation

    class Meta:
        model = DeliveryDetail
        fields = ['id', 'order', 'address', 'address_details', 'expected_delivery_date', 'delivery_charges', 'platform_price', 'overall_price']
        read_only_fields = ['expected_delivery_date', 'overall_price']

    def __init__(self, *args, **kwargs):
        """
        Initialize the serializer and dynamically set the queryset for the `address` field.
        """
        super().__init__(*args, **kwargs)
        if 'request' in self.context:
            user = self.context['request'].user
            self.fields['address'].queryset = Address.objects.filter(user=user)  # Filter addresses for the logged-in user

    def validate(self, data):
        """
        Ensure either `address` or `address_details` is provided.
        """
        if not data.get('address') and not data.get('address_details'):
            raise serializers.ValidationError("Either `address` or `address_details` must be provided.")
        return data

    def handle_address_creation(self, validated_data):
        """
        Handle the creation of a new address if `address_details` are provided.
        """
        address = validated_data.pop('address', None)
        address_details = validated_data.pop('address_details', None)

        if address_details:
            # Create a new address if `address_details` are provided
            address = Address.objects.create(user=self.context['request'].user, **address_details)

        return address

    def create(self, validated_data):
        """
        Create a new `DeliveryDetail` instance and handle dynamic address creation.
        """
        address = self.handle_address_creation(validated_data)  # Create address if necessary
        return DeliveryDetail.objects.create(address=address, **validated_data)

    def update(self, instance, validated_data):
        """
        Update an existing `DeliveryDetail` instance and handle dynamic address creation.
        """
        address = self.handle_address_creation(validated_data)  # Create address if necessary

        if address:
            instance.address = address  # Update the instance's address

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance




from rest_framework import serializers

class RetryPaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(help_text="The ID of the order to retry payment for")
    callback_url = serializers.URLField(
        help_text="The URL to which Razorpay will redirect after payment"
    )

    def validate(self, data):
        """
        Add any custom validation logic if needed.
        """
        if not data.get('callback_url'):
            raise serializers.ValidationError(
                {"callback_url": "This field is required."}
            )
        return data
