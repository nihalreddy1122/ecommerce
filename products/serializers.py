from rest_framework import serializers
from .models import Category, Attribute, AttributeValue, Product, ProductVariant, ProductImage
from rest_framework.exceptions import ValidationError

# ================================
# Category Serializer
# ================================
class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    icon = serializers.ImageField(read_only=True)
    products = serializers.SerializerMethodField()  # Fetch related products

    class Meta:
        model = Category
        fields = ['id', 'banners','name', 'slug', 'parent', 'subcategories', 'icon', 'products']

    def get_subcategories(self, obj):
        return CategorySerializer(obj.subcategories.all(), many=True).data

    def get_products(self, obj):
        # Use the correct related_name: 'products'
        products = obj.products.all()
        return ProductSerializer(products, many=True).data


class CategorySerializernavbar(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    icon = serializers.ImageField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'subcategories', 'icon']

    def get_subcategories(self, obj):
        # Use CategorySerializernavbar recursively
        return CategorySerializernavbar(obj.subcategories.all(), many=True).data
    
# ================================
# Attribute and Attribute Value Serializers
# ================================
class AttributeValueSerializer(serializers.ModelSerializer):
    attribute = serializers.CharField(source="attribute.name", read_only=True)

    class Meta:
        model = AttributeValue
        fields = ['id','attribute', 'attribute', 'value', 'slug']

class AttributeSerializer(serializers.ModelSerializer):
    values = AttributeValueSerializer(many=True, read_only=True)

    class Meta:
        model = Attribute
        fields = ['id', 'name', 'slug', 'values']

# ================================
# Product Image Serializer
# ================================
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image']

# ================================
# Product Variant Serializer
# ================================

from .models import VariantImage

class VariantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantImage
        fields = ['id', 'product_variant', 'image']


class ProductVariantSerializer(serializers.ModelSerializer):
    attributes = AttributeValueSerializer(many=True, read_only=True)  # ✅ Return full attribute details
    attribute_ids = serializers.PrimaryKeyRelatedField(
        queryset=AttributeValue.objects.all(), many=True, write_only=True
    )
    discount_percentage = serializers.ReadOnlyField()
    images = VariantImageSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'attributes', 'attribute_ids', 'base_price', 'offer_price',
            'discount_percentage', 'stock', 'sku', 'images'
        ]
        extra_kwargs = {
            'attribute_ids': {'write_only': True}  # ✅ Hide attribute_ids in response, use for input only
        }

    def create(self, validated_data):
        attributes = validated_data.pop('attribute_ids', [])  # ✅ Extract attributes (write-only)
        product = validated_data.get('product')

        
        existing_variants = ProductVariant.objects.filter(product=product)
        for variant in existing_variants:
            existing_attribute_ids = set(variant.attributes.values_list('id', flat=True))
            new_attribute_ids = set(attr.id for attr in attributes)
            if existing_attribute_ids == new_attribute_ids:
                raise ValidationError("A product variant with the same attribute values already exists.")

       
        product_variant = ProductVariant.objects.create(**validated_data)
        product_variant.attributes.set(attributes)  # ✅ Set ManyToMany attributes

        
        product.stock += product_variant.stock

        
        if product.is_cancelable and not product.cancellation_stage:
            product.cancellation_stage = "Default Stage"

        product.save()
        return product_variant

    def update(self, instance, validated_data):
        attributes = validated_data.pop('attribute_ids', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # ✅ Update attributes if provided
        if attributes:
            instance.attributes.set(attributes)

        return instance



# ================================
# Product Serializer
# ================================
from rest_framework import serializers
from .models import Product
from .serializers import ProductVariantSerializer, ProductImageSerializer

class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    product_id = serializers.IntegerField(source='id', read_only=True)  
    sku = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id','product_id' ,'name', 'sku','slug', 'description', 'additional_details', 'category',
            'thumbnail', 'is_returnable', 'max_return_days', 'is_cancelable', 'cancellation_stage', 'is_cod_allowed',
            'created_at', 'updated_at', 'variants', 'images', 'stock',
        ]

    def validate(self, data):
        # Validate is_returnable and max_return_days
        if data.get('is_returnable') and not data.get('max_return_days'):
            raise serializers.ValidationError({"max_return_days": "This field is required if the product is returnable."})

        # Validate is_cancelable and cancellation_stage
        if data.get('is_cancelable') and not data.get('cancellation_stage'):
            raise serializers.ValidationError({"cancellation_stage": "This field is required if the product is cancelable."})
        
        return data


class RelatedProductSerializer(serializers.ModelSerializer):
    offer_price = serializers.SerializerMethodField()  # Fetch the offer price dynamically
    base_price = serializers.SerializerMethodField()  # Fetch the base price dynamically
    product_id = serializers.IntegerField(source='id', read_only=True)  # Added product_id field

    class Meta:
        model = Product
        fields = [
            'id','product_id' ,'name', 'category',
            'thumbnail',  'offer_price', 'base_price',
        ]
    def get_offer_price(self, obj):
        # Fetch the offer price from the first variant if available
        if obj.variants.exists():
            return obj.variants.first().offer_price  # Use offer_price from the variant
        return None  # Return None if no variants

    def get_base_price(self, obj):
        # Fetch the base price from the first variant if available
        if obj.variants.exists():
            return obj.variants.first().base_price  # Use base_price from the variant
        return None  # Return None if no variants


# App: products/serializers.py

from rest_framework import serializers
from .models import FeaturedProduct

class FeaturedProductSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='vendor.shop_name', read_only=True)
    product_id = serializers.IntegerField(source='id', read_only=True)  # Added product_id field

    class Meta:
        model = FeaturedProduct
        fields = ['id', 'product_id', 'added_at','store_name']
        read_only_fields = ['vendor']  # Prevent vendor from being passed in the request


from rest_framework import serializers
from .models import Product

class ProductFilterSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    store_name = serializers.CharField(source='vendor.shop_name', read_only=True)
    price = serializers.SerializerMethodField()  # Fetch the offer price dynamically
    base_price = serializers.SerializerMethodField()  # Fetch the base price dynamically
    attributes = ProductVariantSerializer(source="variants", many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'store_name', 'name', 'category', 'category_name', 'thumbnail', 'price', 'base_price', 'stock','attributes']

    def get_price(self, obj):
        # Fetch the offer price from the first variant if available
        if obj.variants.exists():
            return obj.variants.first().offer_price  # Use offer_price from the variant
        return None  # Return None if no variants

    def get_base_price(self, obj):
        # Fetch the base price from the first variant if available
        if obj.variants.exists():
            return obj.variants.first().base_price  # Use base_price from the variant
        return None  # Return None if no variants


from rest_framework import serializers
from .models import Product

class NewArrivalsSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    product_id = serializers.IntegerField(source='id', read_only=True)  # Added product_id field
    vendor_name = serializers.CharField(source='vendor.shop_name', read_only=True)
    base_price = serializers.SerializerMethodField()
    offer_price = serializers.SerializerMethodField()  # Fetch price dynamically from the first variant
    
    class Meta:
        model = Product
        fields = [
            'id',
            'product_id',
            'name',
            'vendor_name',
            'category',
            'category_name',
            'thumbnail',
            'created_at',
            'stock',
            'offer_price',
            'base_price',
        ]

    def get_offer_price(self, obj):
        # Fetch the price from the first variant if available
        if obj.variants.exists():
            return obj.variants.first().offer_price  # Use offer_price field from the variant
        return None  # Return None if no variants are available

    def get_base_price(self, obj):
        # Fetch the base price from the first variant if available
        if obj.variants.exists():
            return obj.variants.first().base_price  # Use base_price field from the variant
        return None  # Return None if no variants are available
    



from rest_framework import serializers
from products.models import Category

class StoreCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'subcategories', 'icon']  # Include only the fields you need



from rest_framework import serializers
from .models import LimitedEditionProduct

class LimitedEditionProductSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id', read_only=True)  # Added product_id field
    product_name = serializers.CharField(source='product.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.shop_name', read_only=True)
    thumbnail = serializers.ImageField(source='product.thumbnail', read_only=True)
    leaf_category_name = serializers.CharField(source='product.category.name', read_only=True)
    base_price = serializers.SerializerMethodField()
    offer_price = serializers.SerializerMethodField()

    class Meta:
        model = LimitedEditionProduct
        fields = [
            'id',"product_id", 'product', 'product_name', 'vendor', 'vendor_name',
            'thumbnail', 'leaf_category_name', 'limited_stock',
            'available_from', 'available_until', 'base_price', 'offer_price',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('vendor', 'created_at', 'updated_at')  # ✅ Fix vendor field

    def validate(self, data):
        user = self.context['request'].user
        product = data['product']

        # Get the vendor from the authenticated user
        try:
            vendor = user.vendor_details
        except AttributeError:
            raise serializers.ValidationError("You are not a registered vendor.")

        # Ensure the product belongs to the vendor
        if product.vendor != vendor:
            raise serializers.ValidationError("The product does not belong to you.")

        # If the user is not an admin, ensure they can only manage their own products
        if not user.is_staff and product.vendor != vendor:
            raise serializers.ValidationError("You can only manage products owned by your account.")

        return data

    def get_base_price(self, obj):
        """
        Fetch the base price from the first available product variant.
        """
        first_variant = obj.product.variants.first()
        return first_variant.base_price if first_variant else None

    def get_offer_price(self, obj):
        """
        Fetch the offer price from the first available product variant.
        """
        first_variant = obj.product.variants.first()
        return first_variant.offer_price if first_variant else None




