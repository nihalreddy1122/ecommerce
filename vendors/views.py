from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import VendorDetails
from .serializers import VendorDetailsSerializer
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
import mimetypes
import os
from django.conf import settings
from cart_orders.models import OrderItem
from .serializers import OrderItemSerializer

class VendorDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve vendor details."""
        vendor_details = get_object_or_404(VendorDetails, user=request.user)
        serializer = VendorDetailsSerializer(vendor_details)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create or update vendor details."""
        vendor_details, created = VendorDetails.objects.get_or_create(user=request.user)
        serializer = VendorDetailsSerializer(vendor_details, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """Partially update vendor details."""
        vendor_details = get_object_or_404(VendorDetails, user=request.user)
        serializer = VendorDetailsSerializer(vendor_details, data=request.data, partial=True,)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def serve_media(request, path):
    """Serve media files."""
    full_path = os.path.join(settings.MEDIA_ROOT, path)

    # Restrict access to files outside MEDIA_ROOT
    if not full_path.startswith(settings.MEDIA_ROOT):
        raise Http404("File not found or access denied.")

    if not os.path.exists(full_path):
        raise Http404("The requested file does not exist.")

    # Guess the MIME type based on the file extension
    content_type, _ = mimetypes.guess_type(full_path)
    if content_type is None:
        content_type = "application/octet-stream"  # Fallback if type can't be guessed

    # Serve the file securely
    with open(full_path, 'rb') as file:
        return FileResponse(file, content_type=content_type)


class VendorPaidOrderItemsView(APIView):
    """
    Endpoint to get a list of order items with payment_status='paid' for the vendor.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the authenticated vendor from the request
        user = request.user

        # Ensure the user is a vendor
        if user.user_type != 'vendor':
            raise PermissionDenied("You do not have permission to access this resource.")
        print(user.vendor_profile, "vendor profile")
        # Fetch the order items with payment_status='paid' for this vendor
        VendorDetails = user.vendor_details  # Assuming vendor_profile is linked to VendorDetails
        print(VendorDetails, "vendor details")  
        # Fetch the order items with payment_status='paid' for this vendor
        paid_order_items = OrderItem.objects.filter(vendor=VendorDetails, payment_status='paid')

        # Serialize the data
        serializer = OrderItemSerializer(paid_order_items, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    



from datetime import date, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from cart_orders.models import OrderItem

class VendorDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            vendor = request.user.vendor_details 
        except:
            return Response({"vendor details"}) # Ensure this matches your relationship

        # Fetch OrderItems linked to the vendor
        order_items = OrderItem.objects.filter(product_variant__product__vendor=vendor)

        # Total Orders
        total_orders = order_items.values('order').distinct().count()

        # Earnings for the Week
        week_start = date.today() - timedelta(days=7)
        weekly_earnings = order_items.filter(
            order__created_at__gte=week_start,
            order__payment_status='paid'
        ).aggregate(total=Sum('order__total_price'))['total'] or 0

        # Earnings for the Day
        daily_earnings = order_items.filter(
            order__created_at__date=date.today(),
            order__payment_status='paid'
        ).aggregate(total=Sum('order__total_price'))['total'] or 0

        data = {
            "total_orders": total_orders,
            "total_earnings_week": weekly_earnings,
            "total_earnings_day": daily_earnings,
        }
        return Response(data)



class VendorOrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_item_id):
        """
        Retrieve the current status of the order item.
        """
        order_item = get_object_or_404(OrderItem, id=order_item_id)
        return Response({
            "order_item_id": order_item.id,
            "product_name": order_item.product_variant.product.name,
            "current_status": order_item.order_status,
            "updated_at": order_item.updated_at,
        }, status=status.HTTP_200_OK)

    def patch(self, request, order_item_id):
        """
        Update the status of the order item.
        """
        order_item = get_object_or_404(OrderItem, id=order_item_id)
        new_status = request.data.get("new_status")

        if not new_status:
            return Response({"error": "New status is required."}, status=status.HTTP_400_BAD_REQUEST)

        if order_item.update_status(new_status):
            return Response({"message": f"Order item status updated to {new_status}."}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid status transition."}, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class OrderStatusOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Define the available order statuses
        status_options = [
            {"value": "ready_to_pick_up", "label": "Ready to Pick Up"},
            {"value": "packed", "label": "Packed"},
        ]
        return Response(status_options)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import VendorDetails, StoreImage
from .serializers import VendorShopSerializer, StoreImageSerializer

class VendorShopListView(APIView):
    """
    View to fetch all vendors with their shop names and logos.
    """
    permission_classes = []  # Open to all users

    def get(self, request):
        try:
            vendors = VendorDetails.objects.all()
            serializer = VendorShopSerializer(vendors, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StoreImageView(APIView):
    """
    View to manage store images for a specific vendor.
    """
    def get(self, request, vendor_id):
        """
        Retrieve all store images for a specific vendor.
        """
        vendor = get_object_or_404(VendorDetails, pk=vendor_id)
        images = vendor.store_images.all()
        serializer = StoreImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, vendor_id):
        """
        Add store images to a specific vendor.
        Ensures exactly 4 images are provided.
        """
        vendor = get_object_or_404(VendorDetails, pk=vendor_id)

        if 'images' not in request.FILES:
            return Response({"error": "No images uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        images = request.FILES.getlist('images')

        if len(images) != 4:
            return Response({"error": "Exactly 4 images are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Delete existing images and replace with new ones
        StoreImage.objects.filter(vendor=vendor).delete()

        for image in images:
            StoreImage.objects.create(vendor=vendor, image=image)

        return Response({"message": "Store images uploaded successfully"}, status=status.HTTP_201_CREATED)

from products.serializers import ProductSerializer
from products.models import Product  # Add this line
# customer/views.py
# customer/views.py
class ProductsByShopNameView(APIView):
    permission_classes = []

    def get(self, request, shop_name):
        try:
            vendor = VendorDetails.objects.get(shop_name=shop_name)
            products = Product.objects.filter(vendor=vendor)

            # Add category filtering
            category_id = request.query_params.get('category_id')
            if category_id:
                products = products.filter(category__id=category_id)

            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except VendorDetails.DoesNotExist:
            return Response({"error": "Shop not found."}, status=status.HTTP_404_NOT_FOUND)
        

# customer/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from vendors.models import VendorDetails
from products.models import Category, Product  # Add Product import
from products.serializers import CategorySerializer

class storecategoryview(APIView):
    permission_classes = [AllowAny]

    def get(self, request, shop_name):
        try:
            # Get the vendor
            vendor = VendorDetails.objects.get(shop_name=shop_name)
            
            # Get categories that HAVE PRODUCTS in this store
            categories = Category.objects.filter(
                products__vendor=vendor  # Filter categories with products from this vendor
            ).distinct()  # Remove duplicate categories
            
            serializer = CategorySerializer(categories, many=True)
            
            return Response({
                "vendor": {
                    "shop_name": vendor.shop_name,
                    "shop_logo": vendor.shop_logo.url if vendor.shop_logo else None
                },
                "categories": serializer.data
            }, status=status.HTTP_200_OK)
            
        except VendorDetails.DoesNotExist:
            return Response({"error": "Store not found."}, status=status.HTTP_404_NOT_FOUND)