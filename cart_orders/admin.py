from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem, SubOrder

# ================================
# Inline Classes for Related Models
# ================================

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['product_variant', 'quantity', 'get_subtotal']

    def get_subtotal(self, obj):
        return obj.quantity * obj.product_variant.offer_price
    get_subtotal.short_description = 'Subtotal'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_variant', 'quantity', 'price', 'get_total']

    def get_total(self, obj):
        if obj.quantity is not None and obj.price is not None:
            return obj.quantity * obj.price
        return "N/A"  # Return a placeholder value if data is missing
    get_total.short_description = 'Total'

class SubOrderInline(admin.TabularInline):
    model = SubOrder
    extra = 0
    readonly_fields = ['vendor', 'subtotal']

# ================================
# Admin Classes
# ================================

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'updated_at']
    inlines = [CartItemInline]
    search_fields = ['user__email']
    list_filter = ['created_at', 'updated_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'total_price', 'payment_status', 'created_at', 'updated_at']
    inlines = [OrderItemInline, SubOrderInline]
    search_fields = ['customer__email']
    list_filter = ['payment_status', 'created_at', 'updated_at']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'product_variant', 'quantity', 'get_subtotal']
    search_fields = ['cart__user__email', 'product_variant__sku']
    list_filter = ['cart__created_at']

    def get_subtotal(self, obj):
        return obj.quantity * obj.product_variant.offer_price
    get_subtotal.short_description = 'Subtotal'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product_variant', 'quantity', 'price', 'get_total']
    search_fields = ['order__customer__email', 'product_variant__sku']
    list_filter = ['order__created_at']

    def get_total(self, obj):
        return obj.quantity * obj.price
    get_total.short_description = 'Total'


@admin.register(SubOrder)
class SubOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'vendor', 'subtotal', 'created_at']
    search_fields = ['order__customer__email', 'vendor__user__email']
    list_filter = ['created_at']
