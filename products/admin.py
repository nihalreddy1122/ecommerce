from django.contrib import admin
from .models import Category, Attribute, AttributeValue, Product, ProductVariant, ProductImage, FeaturedProduct, VariantImage, LimitedEditionProduct

# ================================
# Inline Admin for Related Models
# ================================

class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class VariantImageInline(admin.TabularInline):
    model = VariantImage
    extra = 1

# ================================
# Admin Models
# ================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'banners','slug')  # Removed created_at and updated_at
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('parent',)

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')  # Removed created_at and updated_at
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'attribute', 'value', 'slug')  # Removed created_at and updated_at
    search_fields = ('value', 'attribute__name')
    list_filter = ('attribute',)
    prepopulated_fields = {'slug': ('value',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'vendor', 'category')  # Removed created_at and updated_at
    search_fields = ('name', 'vendor__user__email', 'category__name')
    list_filter = ('category', 'vendor')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline, ProductImageInline]

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'base_price', 'offer_price', 'stock', 'sku', 'discount_percentage')  # Removed created_at and updated_at
    search_fields = ('product__name', 'sku')
    list_filter = ('product',)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image')  # Removed created_at and updated_at
    search_fields = ('product__name',)

@admin.register(VariantImage)
class VariantImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_variant', 'image')  # Removed created_at and updated_at
    search_fields = ('product_variant__product__name',)

# ================================
# Featured Product Admin
# ================================

@admin.register(FeaturedProduct)
class FeaturedProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'vendor', 'product', 'added_at')
    search_fields = ('vendor__user__email', 'product__name')
    list_filter = ('vendor', 'added_at')


@admin.register(LimitedEditionProduct)
class LimitedEditionProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'vendor', 'limited_stock', 'available_from', 'available_until', 'created_at')
    list_filter = ('vendor', 'available_from', 'available_until')
    search_fields = ('product__name', 'vendor__shop_name')
    readonly_fields = ('created_at', 'updated_at')