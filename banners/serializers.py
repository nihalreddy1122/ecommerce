from rest_framework import serializers
from .models import Banner
from products.models import Category
from vendors.models import VendorDetails

class BannerSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    store_name = serializers.CharField(source='store.shop_name', read_only=True)

    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'description', 'image', 'banner_type', 'category', 'category_name',
            'store', 'store_name', 'external_url', 'position', 'priority', 'is_active', 'created_at'
        ]
