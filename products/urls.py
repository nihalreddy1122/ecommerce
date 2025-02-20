from django.urls import path
from .views import (
    CategoryListCreateView,
    CategoryDetailView,
    AttributeListCreateView, 
    AttributeDetailView,
    AttributeValueListCreateView, 
    AttributeValueDetailView,
    ProductListCreateView, 
    ProductDetailView,
    ProductVariantListCreateView, 
    ProductVariantDetailView,
    ProductImageListCreateView, 
    ProductImageDetailView,
    LeafCategoriesByParentView,
    VariantImageDetailView,
    FeaturedProductListCreateView,
    ProductFilterByCategoryView,
    NewArrivalsView,
    ProductListView,
    CategoryHierarchyView,
    ProductsByCategoryView,
    CategoryWithProducts,
    LeafCategoriesWithProductsOnlyView,
    LeafCategoriesByShopView,
    ProductsByShopAndCategoryView,
    LimitedEditionProductListCreateView, 
    LimitedEditionProductDetailView,
    AllLimitedEditionProductsView, 
    ProductFilterView,

    

    

)

urlpatterns = [
    # Category URLs
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<int:parent_id>/leaf/', LeafCategoriesByParentView.as_view(), name='leaf-categories'),

    # Attribute URLs
    path('attributes/', AttributeListCreateView.as_view(), name='attribute-list-create'),
    path('attributes/<int:pk>/', AttributeDetailView.as_view(), name='attribute-detail'),
    path('attribute-values/', AttributeValueListCreateView.as_view(), name='attribute-value-list-create'),
    path('attribute-values/<int:pk>/', AttributeValueDetailView.as_view(), name='attribute-value-detail'),

    # Product URLs
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),

    # Product Variant URLs
    path('variants/', ProductVariantListCreateView.as_view(), name='variant-list-create'),
    path('variants/<int:pk>/', ProductVariantDetailView.as_view(), name='variant-detail'),
    path('variants/images/<int:pk>/', VariantImageDetailView.as_view(), name='variant-image-detail'),

    # Product Image URLs
    path('images/', ProductImageListCreateView.as_view(), name='image-list-create'),
    path('images/<int:pk>/', ProductImageDetailView.as_view(), name='image-detail'),

    path('featured-products/', FeaturedProductListCreateView.as_view(), name='featured-products'),
    path('featured-products/<int:product_id>/', FeaturedProductListCreateView.as_view(), name='featured-product-delete'),

    
    path('products/filter/', ProductFilterByCategoryView.as_view(), name='product-filter'),
    
    path('products/new-arrivals/', NewArrivalsView.as_view(), name='new-arrivals'),

    path('filter-category-products/', ProductListView.as_view(), name='filter-category-products'),

    path('categories/hierarchy/', CategoryHierarchyView.as_view(), name='category-hierarchy'),
    path('categories/hierarchy/<int:category_id>/', CategoryHierarchyView.as_view(), name='category-hierarchy-detail'),

    path('categories/<int:category_id>/products/', ProductsByCategoryView.as_view(), name='products-by-leaf-category'),

    path('categories-with-products/', CategoryWithProducts.as_view(), name='categories-with-products'),
    path('categories-with-products/<int:category_id>/', CategoryWithProducts.as_view(), name='categories-with-products-by-id'),
    
    path('leaf-categories-with-products/', LeafCategoriesWithProductsOnlyView.as_view(), name='leaf-categories-with-products'),




    path('stores/<str:shop_name>/leaf-categories/', LeafCategoriesByShopView.as_view(), name='leaf-categories-by-shop'),
    path('stores/<str:shop_name>/categories/<int:category_id>/products/', ProductsByShopAndCategoryView.as_view(), name='products-by-shop-and-category'),


    # List and create Limited Edition products
    path('limited-edition-products/', LimitedEditionProductListCreateView.as_view(), name='limited-edition-list-create'),
    
    # Retrieve, update, or delete a specific Limited Edition product
    path('limited-edition-products/<int:pk>/', LimitedEditionProductDetailView.as_view(), name='limited-edition-detail'),
    


    path('limited-edition/', AllLimitedEditionProductsView.as_view(), name='all-limited-edition-products'),

    path('filter/', ProductFilterView.as_view(), name='product-filter'),


]
