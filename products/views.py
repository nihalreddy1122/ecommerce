from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Category, Attribute, AttributeValue, Product, ProductVariant, ProductImage
from .serializers import (
    CategorySerializer,
    AttributeSerializer,
    AttributeValueSerializer,
    ProductSerializer,
    ProductVariantSerializer,
    ProductImageSerializer
)

# ================================
# Category Views
# ================================
class CategoryListCreateView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

class CategoryDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

# ================================
# Leaf Category Views
# ================================

class LeafCategoriesByParentView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, parent_id):
        try:
            parent_category = Category.objects.get(id=parent_id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found.'}, status=404)

        # Fetch all leaf categories under the selected category
        leaf_categories = parent_category.get_leaf_categories()
        serializer = CategorySerializer(leaf_categories, many=True)
        return Response(serializer.data)

# ================================
# Attribute Views
# ================================
class AttributeListCreateView(ListCreateAPIView):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

class AttributeDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

class AttributeValueListCreateView(ListCreateAPIView):
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

class AttributeValueDetailView(RetrieveUpdateDestroyAPIView):
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

# ================================
# Product Views
# ================================
class ProductListCreateView(ListCreateAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        # Filter products by the vendor of the logged-in user
        return Product.objects.filter(vendor=self.request.user.vendor_details)

    def get_permissions(self):
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        # Save the product with the vendor set to the logged-in user's vendor details
        serializer.save(vendor=self.request.user.vendor_details)


class ProductDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

# ================================
# Product Variant Views
# ================================
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .models import ProductVariant, VariantImage
from .serializers import ProductVariantSerializer
from rest_framework import serializers

class ProductVariantListCreateView(ListCreateAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        product_variant = serializer.save()
        images = self.request.FILES.getlist('images')
        for image in images:
            VariantImage.objects.create(product_variant=product_variant, image=image)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except serializers.ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)


class ProductVariantDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        # Update the product variant
        product_variant = serializer.save()

        # Handle nested image updates
        images = self.request.FILES.getlist('images')  # Expect multiple files with key 'images'
        if images:
            # Clear existing images
            VariantImage.objects.filter(product_variant=product_variant).delete()
            # Add new images
            for image in images:
                VariantImage.objects.create(product_variant=product_variant, image=image)



# ================================
# Product Image Views
# ================================
class ProductImageListCreateView(ListCreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

class ProductImageDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]


from rest_framework.generics import RetrieveDestroyAPIView
from .models import VariantImage
from .serializers import VariantImageSerializer

class VariantImageDetailView(RetrieveDestroyAPIView):
    """
    Allows retrieving and deleting a specific VariantImage by its primary key.
    """
    queryset = VariantImage.objects.all()
    serializer_class = VariantImageSerializer




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import FeaturedProduct, Product
from .serializers import FeaturedProductSerializer
from vendors.models import VendorDetails
from django.core.exceptions import ValidationError

class FeaturedProductListCreateView(APIView):
    def get(self, request):
        # Fetch the vendor for the logged-in user
        try:
            vendor = VendorDetails.objects.get(user=request.user)
        except VendorDetails.DoesNotExist:
            return Response({"detail": "Vendor not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Get all featured products for the logged-in vendor
        featured_products = FeaturedProduct.objects.filter(vendor=vendor)
        serializer = FeaturedProductSerializer(featured_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Fetch the vendor for the logged-in user
        try:
            vendor = VendorDetails.objects.get(user=request.user)
        except VendorDetails.DoesNotExist:
            return Response({"detail": "Vendor not found."}, status=status.HTTP_404_NOT_FOUND)

        # Validate the product belongs to the logged-in vendor
        product_id = request.data.get('product')
        try:
            product = Product.objects.get(id=product_id, vendor=vendor)
        except Product.DoesNotExist:
            return Response({"detail": "This product does not belong to you."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and save the featured product
        if vendor.featured_products.count() >= 10:
            return Response({"detail": "You can only have up to 10 featured products."}, status=status.HTTP_400_BAD_REQUEST)

        featured_product = FeaturedProduct(vendor=vendor, product=product)
        try:
            featured_product.save()
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FeaturedProductSerializer(featured_product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, product_id):
        """
        Remove a featured product.
        """
        try:
            vendor = VendorDetails.objects.get(user=request.user)
        except VendorDetails.DoesNotExist:
            return Response({"detail": "Vendor not found."}, status=status.HTTP_404_NOT_FOUND)

        featured_product = get_object_or_404(FeaturedProduct, product_id=product_id, vendor=vendor)
        featured_product.delete()

        return Response({"message": "Featured product removed successfully."}, status=status.HTTP_204_NO_CONTENT)




from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import Product, Category
from .serializers import ProductFilterSerializer


class ProductPagination(PageNumberPagination):
    """
    Custom pagination class for product filtering.
    """
    page_size = 6  # Number of products per page
    page_size_query_param = 'page_size'  # Allow users to set page size via query
    max_page_size = 100  # Maximum products per page


class ProductFilterByCategoryView(ListAPIView):
    """
    API view to filter products by category, including subcategories.
    """
    serializer_class = ProductFilterSerializer
    pagination_class = ProductPagination
    permission_classes = []  # Open to all users (no authentication required)

    def get_queryset(self):
        # Get the category ID from the query parameters
        category_id = self.request.query_params.get('category_id')
        if not category_id:
            return Product.objects.none()  # Return an empty queryset if no category ID

        try:
            # Get the selected category
            category = Category.objects.get(id=category_id)

            # Fetch all subcategories, including the selected category
            subcategories = Category.objects.filter(Q(id=category.id) | Q(parent=category))

            # Return filtered products for the subcategories
            return Product.objects.filter(category__in=subcategories, is_active=True).select_related('category')

        except Category.DoesNotExist:
            return Product.objects.none()  # Return an empty queryset if the category is not found




from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from .models import Product
from .serializers import NewArrivalsSerializer
from datetime import timedelta
from django.utils.timezone import now

class NewArrivalsPagination(PageNumberPagination):
    page_size = 8  # Default number of products per page
    page_size_query_param = 'page_size'  # Allow frontend to set the page size
    max_page_size = 90 # Limit the maximum number of products per page

class NewArrivalsView(ListAPIView):
    serializer_class = NewArrivalsSerializer
    pagination_class = NewArrivalsPagination


    permission_classes = []
    def get_queryset(self):
        # Define the time window for "New Arrivals" (e.g., last 30 days)
        new_arrivals_window = now() - timedelta(days=30)

        # Get products within the new arrivals window
        new_products = Product.objects.filter(created_at__gte=new_arrivals_window).order_by('-created_at')

        # If fewer than the desired count, add older products to fill the gap
        if new_products.count() < self.pagination_class.page_size:
            fallback_products = Product.objects.exclude(id__in=new_products).order_by('-created_at')[:self.pagination_class.page_size - new_products.count()]
            return new_products | fallback_products  # Combine querysets

        return new_products



from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from products.models import Product, Category
from products.serializers import ProductSerializer

class ProductPagination(PageNumberPagination):
    page_size = 8  # Limit to 8 products per page
    page_size_query_param = 'page_size'  # Allow clients to override page size
    max_page_size = 100  # Set a maximum limit for page size

class ProductListView(ListAPIView):
    """
    View to retrieve paginated products, including those from nested subcategories of a root category.
    """
    permission_classes = [AllowAny]  # Allow access to all users
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    def get_queryset(self):
        # Get the root category ID from the request (e.g., query parameter or URL)
        root_category_id = self.request.query_params.get('category_id')
        if not root_category_id:
            return Product.objects.none()  # Return an empty queryset if no category ID is provided

        # Fetch the root category
        root_category = get_object_or_404(Category, id=root_category_id)

        # Get all subcategories, including nested ones
        all_subcategories = root_category.get_all_subcategories()
        all_category_ids = [category.id for category in all_subcategories]
        all_category_ids.append(root_category.id)  # Include the root category itself

        # Query products for these categories
        return Product.objects.filter(category_id__in=all_category_ids, is_active=True)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Category
from .serializers import CategorySerializernavbar

class CategoryHierarchyView(APIView):
    """
    Fetch the entire category hierarchy down to the leaf level.
    """
    permission_classes = [AllowAny]

    def get(self, request, category_id=None):
        if category_id:
            # Fetch the selected category
            category = get_object_or_404(Category, id=category_id)

            # Return the selected category and all its subcategories
            return Response(CategorySerializernavbar(category).data, status=status.HTTP_200_OK)
        else:
            # Fetch all root categories and their subcategories
            root_categories = Category.objects.filter(parent=None)
            return Response(CategorySerializernavbar(root_categories, many=True).data, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Category, Product
from .serializers import ProductSerializer

class ProductsByCategoryView(APIView):
    """
    Fetch products for a specific category (including root, subcategory, or leaf category).
    """
    permission_classes = [AllowAny]

    def get(self, request, category_id):
        # Fetch the category
        category = get_object_or_404(Category, id=category_id)

        # Fetch products under the specified category
        products = Product.objects.filter(category=category, is_active=True)
        serialized_products = ProductSerializer(products, many=True).data

        return Response({
            "category": {
                "id": category.id,
                "name": category.name,
                "slug": category.slug
            },
            "products": serialized_products
        }, status=status.HTTP_200_OK)



from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from .models import Category
from .serializers import CategorySerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from products.models import Category

class CategoryWithProducts(APIView):
    """
    API to display categories that have products in their hierarchy,
    filtering recursively from the leaf categories. 
    Supports filtering by category ID.
    """
    permission_classes = [AllowAny]

    def get(self, request, category_id=None):
        def filter_categories_with_products(category):
            """
            Recursively check if a category or any of its subcategories have products.
            """
            # If it's a leaf category, check if it has products
            if not category.subcategories.exists():
                return category.products.exists()

            # Check recursively for subcategories
            has_products = False
            valid_subcategories = []
            for sub in category.subcategories.all():
                if filter_categories_with_products(sub):
                    has_products = True
                    valid_subcategories.append(sub)

            # Filter subcategories to only include those with products
            category._filtered_subcategories = valid_subcategories
            return has_products

        # If category ID is provided, fetch that category
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            categories = [category] if filter_categories_with_products(category) else []
        else:
            # Get all root categories
            categories = [cat for cat in Category.objects.filter(parent=None) if filter_categories_with_products(cat)]

        # Serialize the filtered categories with their filtered subcategories
        def serialize_category(category):
            return {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "parent": category.parent.id if category.parent else None,
                "subcategories": [serialize_category(sub) for sub in getattr(category, '_filtered_subcategories', [])],
                "icon": category.icon.url if category.icon else None,
                "banners": category.banners.url if category.banners else None
            }

        response_data = [serialize_category(cat) for cat in categories]
        return Response(response_data)





class LeafCategoriesWithProductsOnlyView(APIView):
    """
    API to display only the leaf categories that have products.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Fetch only leaf categories that have associated products
        leaf_categories = Category.objects.filter(subcategories__isnull=True).annotate(
            product_count=Count('products')
        ).filter(product_count__gt=0)

        # Serialize only the required fields of the leaf categories
        response_data = [
            {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "parent": category.parent.id if category.parent else None,
                "subcategories": [],
                "icon": category.icon.url if category.icon else None
            }
            for category in leaf_categories
        ]

        return Response(response_data)


from products.serializers import StoreCategorySerializer


class LeafCategoriesByShopView(APIView):
    """
    Fetch only the leaf categories related to a specific shop.
    """
    permission_classes = []  # Open to all users

    def get(self, request, shop_name):
        # Fetch the vendor using the shop name
        vendor = get_object_or_404(VendorDetails, shop_name=shop_name)

        # Fetch all products for the given vendor
        products = Product.objects.filter(vendor=vendor)

        # Create a set of categories that are linked to these products
        category_set = set(product.category for product in products if product.category)

        # Filter for leaf categories (categories without subcategories)
        leaf_categories = [category for category in category_set if not category.subcategories.exists()]

        # Serialize the leaf categories using the new serializer
        serialized_categories = StoreCategorySerializer(leaf_categories, many=True).data

        return Response({
            "shop_name": vendor.shop_name,
            "leaf_categories": serialized_categories  # Only leaf categories
        }, status=status.HTTP_200_OK)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from vendors.models import VendorDetails
from products.models import Product, Category
from products.serializers import RelatedProductSerializer

class ProductsByShopAndCategoryView(APIView):
    """
    Fetch all products based on shop name and category, including their variants.
    """
    permission_classes = []  # Adjust permissions as required

    def get(self, request, shop_name, category_id):
        # Fetch the vendor using the shop name
        vendor = get_object_or_404(VendorDetails, shop_name=shop_name)

        # Fetch the category using the category_id
        category = get_object_or_404(Category, id=category_id)

        # Fetch products for the given vendor and category
        products = Product.objects.filter(vendor=vendor, category=category)

        # Serialize the products
        serialized_products = RelatedProductSerializer(products, many=True).data

        return Response({
            "shop_name": vendor.shop_name,
            "category_name": category.name,
            "products": serialized_products,
        }, status=status.HTTP_200_OK)




from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from .models import LimitedEditionProduct
from .serializers import LimitedEditionProductSerializer

class LimitedEditionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import LimitedEditionProduct, Product
from .serializers import LimitedEditionProductSerializer


class LimitedEditionProductListCreateView(ListCreateAPIView):
    """
    List and create limited edition products.
    """
    queryset = LimitedEditionProduct.objects.all().order_by('-available_from')
    serializer_class = LimitedEditionProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Restrict list to products owned by the vendor, unless the user is an admin.
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_staff:  # Non-admins should only see their own products
            queryset = queryset.filter(vendor=user.vendor_details)
        
        # Optional: Filter by available date
        now = self.request.query_params.get('current_date', None)
        if now:
            queryset = queryset.filter(available_from__lte=now, available_until__gte=now)
        
        return queryset

    def perform_create(self, serializer):
        """
        Automatically assign the vendor based on the authenticated user.
        """
        user = self.request.user
        
        # Ensure the user is a vendor
        try:
            vendor = user.vendor_details
        except AttributeError:
            return Response({"detail": "You are not a registered vendor."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer.save(vendor=vendor)  # Auto-set vendor field


class LimitedEditionProductDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete a limited edition product.
    """
    queryset = LimitedEditionProduct.objects.all()
    serializer_class = LimitedEditionProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Restrict access to only the vendor's products unless the user is an admin.
        """
        queryset = super().get_queryset()
        user = self.request.user

        if not user.is_staff:  # Non-admins should only see their own products
            queryset = queryset.filter(vendor=user.vendor_details)

        return queryset

    def delete(self, request, pk):
        """
        Delete a limited edition product if the vendor owns it.
        """
        user = request.user
        
        try:
            vendor = user.vendor_details
        except AttributeError:
            return Response({"detail": "You are not a registered vendor."}, status=status.HTTP_403_FORBIDDEN)

        limited_product = get_object_or_404(LimitedEditionProduct, id=pk, vendor=vendor)
        limited_product.delete()
        
        return Response({"message": "Limited Edition Product removed successfully."}, status=status.HTTP_204_NO_CONTENT)




from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from .models import LimitedEditionProduct
from .serializers import LimitedEditionProductSerializer

class AllLimitedEditionProductsPagination(PageNumberPagination):
    page_size = 10  # Number of products per page
    page_size_query_param = 'page_size'
    max_page_size = 50

class AllLimitedEditionProductsView(ListAPIView):
    """
    View to list all limited edition products across all vendors.
    Accessible to all users.
    """
    queryset = LimitedEditionProduct.objects.select_related(
        'product', 'product__category', 'vendor'
    ).prefetch_related('product__variants').order_by('-available_from')
    
    serializer_class = LimitedEditionProductSerializer
    pagination_class = AllLimitedEditionProductsPagination
    permission_classes = [AllowAny]  # Open to everyone








from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db.models import Q, Prefetch
from .models import Product, ProductVariant
from .serializers import ProductSerializer

class ProductFilterView(APIView):
    
    permission_classes = [AllowAny]

    def get(self, request):
        """
        API to filter products dynamically based on category, price, brand, attributes, and stock availability.
        """
        filters = Q()

        # Category Filter
        category_id = request.GET.get('category_id')
        if category_id:
            filters &= Q(category_id=category_id)

        # Price Range Filter
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        if min_price:
            filters &= Q(variants__offer_price__gte=min_price)
        if max_price:
            filters &= Q(variants__offer_price__lte=max_price)

        # Brand Filter
        brand_id = request.GET.get('brand_id')
        if brand_id:
            filters &= Q(vendor_id=brand_id)

        # Stock Availability Filter
        in_stock = request.GET.get('in_stock')
        if in_stock == 'true':
            filters &= Q(variants__stock__gt=0)

        # ✅ Improved Dynamic Attribute Filtering (Supports Single & Multi-Attribute OR Conditions)
        attribute_filters = request.GET.getlist('attributes')
        if attribute_filters:
            attr_queries = Q()
            for attr_filter in attribute_filters:
                if ':' in attr_filter:
                    _, attr_value = attr_filter.split(':', 1)  # Extract attribute value only
                    attr_queries |= Q(variants__attributes__value=attr_value)  # ✅ Apply OR condition for multiple attributes
            filters &= attr_queries  # Ensures products with ANY matching attribute are included

        # Query Products with Prefetching
        products = Product.objects.filter(filters).prefetch_related(
            Prefetch('variants', queryset=ProductVariant.objects.prefetch_related('attributes'))
        ).distinct()

        # Serialize and Return Response
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)