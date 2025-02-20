from django.urls import path
from .views import *

urlpatterns = [
    path('products/', AllProductsView.as_view(), name='all-products'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('categories/', AllCategoriesView.as_view(), name='all-categories'),
    # Attribute Endpoints
    path('attributes/', AllAttributesView.as_view(), name='all-attributes'),
    path('attributes/<int:pk>/', AttributeDetailView.as_view(), name='attribute-detail'),
    path('products/<int:product_id>/variants/', ProductVariantsView.as_view(), name='product-variants'),

    # Attribute Value Endpoints
    path('attribute-values/', AllAttributeValuesView.as_view(), name='all-attribute-values'),
    path('attribute-values/<int:pk>/', AttributeValueDetailView.as_view(), name='attribute-value-detail'),

    # Product search
    path('products/search/', ProductSearchView.as_view(), name='product-search'),

    # paid orders
    path('order-items/paid/', PaidOrderItemsView.as_view(), name='paid-order-items'),


    # reviews
    path('reviews/', ReviewAPIView.as_view(), name='review-create-get'),
    path('reviews/list/', ReviewListView.as_view(), name='review'),
    path('reviews/<int:review_id>/', ReviewAPIView.as_view(), name='review-delete'),
    path('productreviews/', ProductReviewAPIView.as_view(), name='product'),
    # refund
    path('refund/initiate/', RefundInitiateView.as_view(), name='refund-initiate'),
    path('refunds/<int:refund_id>/', RefundDetailView.as_view(), name='refund-detail'),

    #product 
    #path('products/shop/<str:shop_name>/', ProductsByShopNameView.as_view(), name='products-by-shop-name'),
    path('featured-products/', FeaturedProductListView.as_view(), name='featured-products'),
    path('productslist/', ProductListAPIView.as_view(), name='product-list'),


    #wishlist
    path('wishlist/', WishlistView.as_view(), name="wishlist"),

    #related product
    path('related-products/<int:product_id>/', RelatedProductsView.as_view(), name='related-products'),

    #track order_item
    path('conformed/', ConfirmedOrderItemsView.as_view(), name = 'confirmed-order-items'),
    path('track_order/<int:order_item_id>/', OrderItemStatusDatesView.as_view(), name = 'order_item_tracking'),


]
