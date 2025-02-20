from django.contrib import admin
from .models import PriceRangeCommission, CommissionAndGST

@admin.register(PriceRangeCommission)
class PriceRangeCommissionAdmin(admin.ModelAdmin):
    list_display = ('min_price', 'max_price', 'commission_rate', 'platform_charges')
    search_fields = ('min_price', 'max_price', 'commission_rate', 'platform_charges')
    list_filter = ('commission_rate', 'platform_charges')

@admin.register(CommissionAndGST)
class CommissionAndGSTAdmin(admin.ModelAdmin):
    list_display = ('order_item', 'product', 'vendor', 'product_price', 'commission_rate', 'commission_amount', 'gst_on_commission', 'platform_charges', 'total_deduction', 'vendor_earnings', 'calculated_at')
    search_fields = ('order_item__id', 'product__name', 'vendor__name')
    list_filter = ('commission_rate', 'gst_on_commission', 'platform_charges', 'calculated_at')
    readonly_fields = ('product_price', 'commission_rate', 'commission_amount', 'gst_on_commission', 'platform_charges', 'total_deduction', 'vendor_earnings', 'calculated_at')
