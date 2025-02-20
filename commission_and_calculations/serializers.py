from rest_framework import serializers
from .models import PriceRangeCommission

# ------------------------------------------
# Serializer for PriceRangeCommission Model
# Handles serialization and deserialization of the PriceRangeCommission model
# Used for API interactions (List, Create, Retrieve, Update, Delete)
# ------------------------------------------
class PriceRangeCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceRangeCommission
        # ------------------------------------------
        # Fields to Include:
        # - id: Auto-generated primary key for the price range
        # - min_price: Minimum price of the range
        # - max_price: Maximum price of the range (nullable for open-ended ranges)
        # - commission_rate: Commission percentage for the range
        # - platform_charges: Fixed platform charges for the range
        # ------------------------------------------
        fields = ['id', 'min_price', 'max_price', 'commission_rate', 'platform_charges']
