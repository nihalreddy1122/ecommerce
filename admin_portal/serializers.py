from rest_framework import serializers
from .models import *
from vendors.models import VendorDetails
from authusers.models import *

# Serializer for AdminLog
class AdminLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminLog
        fields = ['id', 'user', 'action', 'timestamp']


# Serializer for VendorPayout
class VendorPayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorPayout
        fields = ['id', 'vendor', 'amount', 'status', 'processed_at', 'created_at']







class VendorDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorDetails
        fields = [
            'shop_name', 'shop_logo', 'bio', 'video',
            'bank_account_number', 'bank_name', 'ifsc_code',
            'id_proof_type', 'id_proof_file', 'is_verified',
            'address', 'state', 'city', 'pincode', 'created_at', 'updated_at'
        ]

class VendorProfileDetailSerializer(serializers.ModelSerializer):
    vendor_details = VendorDetailsSerializer(source='user.vendor_details', read_only=True)

    class Meta:
        model = VendorProfile
        fields = [
            'user', 'shop_address', 'is_approved', 'created_at', 'vendor_details'
        ]
        depth = 1



class VendorProfileUpdateSerializer(serializers.ModelSerializer):
    is_approved = serializers.BooleanField()  # This field is modifiable

    class Meta:
        model = VendorProfile
        fields = ['user', 'shop_address', 'is_approved', 'created_at']
        read_only_fields = ['user', 'shop_address', 'created_at']  # These fields are read-only



class RefundMediaViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundMedia
        fields = ['id', 'media']

class RefundDetailSerializer(serializers.ModelSerializer):
    media = RefundMediaViewSerializer(many=True, read_only=True)
    order_id = serializers.IntegerField(source='order_item.id', read_only=True)
    product_name = serializers.CharField(source='order_item.product.name', read_only=True)
    customer_email = serializers.EmailField(source='order_item.order.customer.email', read_only=True)

    class Meta:
        model = Refund
        fields = [
            'id', 'order_id', 'product_name', 'customer_email', 'reason',
            'amount', 'refund_status', 'refund_initiated_date', 
            'refund_processed_date', 'refund_rejected_date', 
            'refund_implemented_date', 'media', 'created_at'
        ]

class RefundUpdateSerializer(serializers.ModelSerializer):
    refund_status = serializers.ChoiceField(choices=Refund.REFUND_STATUS_CHOICES, required=True)

    class Meta:
        model = Refund
        fields = ['refund_status']

    def update(self, instance, validated_data):
        status = validated_data.get('refund_status')
        current_time = timezone.now()

        # Update timestamps based on the status
        if status == 'processed':
            instance.refund_processed_date = current_time
        elif status == 'rejected':
            instance.refund_rejected_date = current_time
        elif status == 'implemented':
            instance.refund_implemented_date = current_time

        instance.refund_status = status
        instance.save()
        return instance


from rest_framework import serializers
from .models import SoftData

class SoftDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftData
        fields = [
            'id',
            'order',
            'pickup_address',
            'shipping_address',
            'tracking_id',
            'payment_status',
            'weight',
            'dimensions',
            'serviceability_checked',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'tracking_id', 'serviceability_checked', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Custom validation for weight and dimensions.
        """
        weight = data.get('weight')
        dimensions = data.get('dimensions')

        if not weight or weight <= 0:
            raise serializers.ValidationError({'weight': 'Weight must be greater than 0.'})

        if not dimensions or not all(key in dimensions for key in ['length', 'breadth', 'height']):
            raise serializers.ValidationError({
                'dimensions': 'Dimensions must include length, breadth, and height.'
            })

        for dim_key in ['length', 'breadth', 'height']:
            if dimensions[dim_key] <= 0:
                raise serializers.ValidationError({
                    'dimensions': f'{dim_key.capitalize()} must be greater than 0.'
                })

        return data




class WareHouseAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = WareHouseAddress
        fields = '__all__'




from rest_framework import serializers
from .models import XpressBeeShipment, Order, WareHouseAddress



class XpressBeeShipmentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(write_only=True)  # Accept order_id from input
    package_weight = serializers.FloatField()
    package_length = serializers.FloatField()
    package_breadth = serializers.FloatField()
    package_height = serializers.FloatField()
    payment_type = serializers.ChoiceField(choices=["cod", "prepaid", "reverse"], required=False)

    class Meta:
        model = XpressBeeShipment
        exclude = ["created_at", "updated_at"]

    def validate_order_id(self, order_id):
        """
        Ensure the order with the given ID exists.
        """
        try:
            return Order.objects.get(id=order_id)  # Return the Order instance
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order with the given ID does not exist.")

    def validate(self, data):
        """
        Perform any custom validation for other fields if required.
        """
        order = data.get("order")
        data["order_amount"] = order.total_price  # Add order_amount dynamically
        return data

    def create(self, validated_data):
        # Extract the order instance from validated_data
        order = validated_data.pop("order")

        # Assign additional logic like warehouse (if needed)
        try:
            warehouse = WareHouseAddress.objects.get(id=1)
        except WareHouseAddress.DoesNotExist:
            raise serializers.ValidationError("No default warehouse address found. Please set a default warehouse.")

        # Create the shipment instance
        shipment = XpressBeeShipment.objects.create(
            order=order,
            package_weight=validated_data["package_weight"],
            package_length=validated_data["package_length"],
            package_breadth=validated_data["package_breadth"],
            package_height=validated_data["package_height"],
            payment_type=validated_data.get("payment_type", "cod"),
            shipping_charges=validated_data.get("shipping_charges", 0),
            discount=validated_data.get("discount", 0),
            cod_charges=validated_data.get("cod_charges", 0),
            order_amount=validated_data["order_amount"],
            collectable_amount=validated_data.get("collectable_amount", validated_data["order_amount"]),
        )
        return shipment




