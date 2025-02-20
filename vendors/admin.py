from django.contrib import admin
from .models import VendorDetails, StoreImage

@admin.register(VendorDetails)
class VendorDetailsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'shop_name', 'is_verified', 'created_at', 'updated_at')
    search_fields = ('user__email', 'shop_name', 'bank_name', 'ifsc_code')
    list_filter = ('is_verified', 'created_at')

    @admin.action(description='Mark selected vendors as verified')
    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True)

@admin.register(StoreImage)
class StoreImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendor', 'created_at')
    search_fields = ('vendor__shop_name', 'vendor__user__email')
    list_filter = ('created_at',)
