from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from cart_orders.models import OrderItem
from vendors.serializers import OrderItemSerializer
from .models import *
from .serializers import *
from products.models import *
from vendors.models import *
from products.serializers import *
from products.models import Product
from rest_framework import generics


class AllProductsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """Fetch all products with pagination."""
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        """Fetch product details by product ID."""
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AllCategoriesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """Fetch all categories."""
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class AllAttributesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """Fetch all attributes."""
        attributes = Attribute.objects.all()
        serializer = AttributeSerializer(attributes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AttributeDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        """Fetch details of a specific attribute."""
        attribute = get_object_or_404(Attribute, pk=pk)
        serializer = AttributeSerializer(attribute)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AllAttributeValuesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """Fetch all attribute values."""
        attribute_values = AttributeValue.objects.all()
        serializer = AttributeValueSerializer(attribute_values, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AttributeValueDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        """Fetch details of a specific attribute value."""
        attribute_value = get_object_or_404(AttributeValue, pk=pk)
        serializer = AttributeValueSerializer(attribute_value)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


from products.models import ProductVariant
from products.serializers import ProductVariantSerializer

class ProductVariantsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, product_id):
        """Fetch all variants for a specific product."""
        product = get_object_or_404(Product, id=product_id)
        variants = ProductVariant.objects.filter(product=product)
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ProductSearchView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        search_query = request.query_params.get('search', '').strip()
        if not search_query:
            return Response({"detail": "Search query is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Initial search by slug
        search_terms = search_query.split()
        query = Q()
        for term in search_terms:
            query |= Q(slug__icontains=term)
        products = Product.objects.filter(query).distinct()

        # Filter by price range
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        if min_price or max_price:
            variants_query = Q()
            if min_price:
                variants_query &= Q(variants__offer_price__gte=float(min_price))
            if max_price:
                variants_query &= Q(variants__offer_price__lte=float(max_price))
            products = products.filter(variants_query)

        # Filter by attribute values
        attribute_values = request.query_params.getlist('attribute_values')  # Example: ['1', '2', '3']
        if attribute_values:
            products = products.filter(variants__attributes__id__in=attribute_values).distinct()

        # Serialize and return filtered results
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    



# Customer paid orders

class PaidOrderItemsView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access this endpoint

    def get(self, request):
        # Get the currently authenticated user
        user = request.user

        # Filter OrderItems with payment_status "paid" and Orders linked to the user
        paid_items = OrderItem.objects.filter(
            payment_status="paid",
            order__customer=user
        )

        # Serialize the data
        serializer = OrderItemSerializer(paid_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




# Product review
from rest_framework.parsers import MultiPartParser, FormParser

class ReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Allow file uploads

    def post(self, request, *args, **kwargs):
        # Ensure the user is a customer
        if request.user.user_type != 'customer':
            return Response(
                {"detail": "Only customers can create reviews."},
                status=status.HTTP_403_FORBIDDEN
            )

        media_files = request.FILES.getlist('media')  # Extract uploaded files

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(customer=request.user)
            overall_review, _ = OverallReview.objects.get_or_create(product=review.product)
            overall_review.update_average_rating()
            # Save media files
            for media_file in media_files:
                ReviewMedia.objects.create(review=review, media=media_file)

            return Response(ReviewSerializer(review, context={"request": request}).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, *args, **kwargs):
        product_id = request.query_params.get("product")
        if not product_id:
            return Response(
                {"detail": "Product ID is required as a query parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        reviews = Review.objects.filter(product_id=product_id).prefetch_related('media')
        serializer = ReviewSerializer(reviews, many=True, context={"request": request})  # Pass request context
        return Response(serializer.data, status=status.HTTP_200_OK)


    def delete(self, request, *args, **kwargs):
        review_id = kwargs.get("review_id")
        try:
            if request.user.is_admin:
                review = Review.objects.get(id=review_id)
            else:
                review = Review.objects.get(id=review_id, customer=request.user)
    
        except Review.DoesNotExist:
            return Response( 
                {"detail": "Review not found or you are not authorized to delete it."},
                status=status.HTTP_404_NOT_FOUND
            )
        overall_review = OverallReview.objects.get(product=review.product)
        overall_review.update_average_rating()
        review.delete()
        return Response({"detail": "Review deleted successfully."}, status=status.HTTP_200_OK)

class ReviewListView(generics.ListAPIView):
    """
    API endpoint to retrieve a list of reviews.
    
    """
    reviews = Review.objects.prefetch_related('media')
    serializer = ReviewSerializer(reviews, many=True)  # Pass request context
    #return Response(serializer.data, status=status.HTTP_200_OK)
    queryset = Review.objects.prefetch_related('media').order_by('-created_at')
    print(queryset)
    print("hwerbfgsjknbj")
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        reviews = Review.objects.prefetch_related('media')
        serializer = ReviewSerializer(reviews, many=True)  # Pass request context
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def get_serializer_context(self):
        print(self.queryset)
        return {'request': self.request}

class RefundInitiateView(APIView):
    """
    Endpoint to initiate a refund for a given order item.


    """

    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = RefundSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Refund initiated successfully."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductReviewAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        product_id = request.query_params.get("product")
        if not product_id:
            return Response({"detail": "Product ID is required as a query parameter."}, status=400)
        
        reviews = Review.objects.filter(product_id=product_id).prefetch_related('media')
        overall_review = OverallReview.objects.get(product_id=product_id)
        overall_rating = 0
        if overall_review:
            overall_rating = overall_review.average_rating
        review_serializer = ReviewSerializer(reviews, many=True, context={"request": request})
        overall_review_data = {
            "product": product_id,
            "average_rating": overall_rating
        }
        
        return Response({
            "reviews": review_serializer.data,
            "overall_review": overall_review_data
        }, status=200)



class RefundDetailView(APIView):
    def get(self, request, refund_id):
        try:
            refund = Refund.objects.get(id=refund_id)
        except Refund.DoesNotExist:
            return Response({"error": "Refund not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RefundDetailSerializer(refund)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


        

# customers/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from products.models import FeaturedProduct
from .serializers import FeaturedProductDetailSerializer

class FeaturedProductListView(APIView):
    permission_classes = []  # Open to all users (no authentication required)

    def get(self, request):
        # Fetch all featured products
        featured_products = FeaturedProduct.objects.select_related('product', 'vendor').all()
        serializer = FeaturedProductDetailSerializer(featured_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class ProductListAPIView(generics.ListAPIView):
    permission_classes = [] 
    queryset = Product.objects.all()
    serializer_class = ProductDetailsSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



from .models import Wishlist
from .serializers import WishlistSerializer
from products.models import Product

class WishlistView(generics.GenericAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get the user's wishlist."""
        wishlist = Wishlist.objects.filter(user=request.user)
        serializer = self.serializer_class(wishlist, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Add a product to the wishlist."""
        product_id = request.data.get("product_id")
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

        if created:
            return Response({"message": "Product added to wishlist"}, status=status.HTTP_201_CREATED)
        return Response({"message": "Product already in wishlist"}, status=status.HTTP_200_OK)

    def delete(self, request):
        """Remove a product from the wishlist."""
        product_id = request.data.get("product_id")
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        wishlist_item = Wishlist.objects.filter(user=request.user, product=product)
        if wishlist_item.exists():
            wishlist_item.delete()
            return Response({"message": "Product removed from wishlist"}, status=status.HTTP_200_OK)
        return Response({"error": "Product not in wishlist"}, status=status.HTTP_400_BAD_REQUEST)
    
from rest_framework import generics, status
from products.models import Product, Category
from products.serializers import ProductSerializer

class RelatedProductsView(generics.GenericAPIView):
    permission_classes = [AllowAny]  # Change to IsAuthenticated if needed

    def get(self, request, product_id):
        """Fetch products related by category."""
        try:
            # Get the product
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get categories of the given product
        categories = product.category.get_all_subcategories() | {product.category}

        # Initialize product set
        productset = set()

        # Get products in the same categories
        for category in categories:
            related_products = Product.objects.filter(category=category).exclude(id=product_id)
            productset.update(related_products)

        # Serialize the product data
        serializer = RelatedProductSerializer(productset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
