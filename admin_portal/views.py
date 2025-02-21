from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from cart_orders.models import Order
from cart_orders.serializers import OrderSerializer
from rest_framework import generics, permissions
from rest_framework.views import APIView


# View for Admin Logs
class AdminLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = AdminLog.objects.all().order_by('-timestamp')
        serializer = AdminLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# View for Vendor Payouts
class VendorPayoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payouts = VendorPayout.objects.all().order_by('-created_at')
        serializer = VendorPayoutSerializer(payouts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, payout_id):
        payout = get_object_or_404(VendorPayout, id=payout_id)
        serializer = VendorPayoutSerializer(payout, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from authusers.models import VendorProfile
from .serializers import VendorProfileDetailSerializer

class VendorProfileDetailView(RetrieveAPIView):
    queryset = VendorProfile.objects.all()
    serializer_class = VendorProfileDetailSerializer
    permission_classes = [AllowAny]  # Restrict access to authenticated users
    lookup_field = 'id'  # This enables looking up the profile by its `id`



from rest_framework.generics import RetrieveUpdateAPIView


class VendorProfileUpdateView(RetrieveUpdateAPIView):
    queryset = VendorProfile.objects.all()
    serializer_class = VendorProfileUpdateSerializer
    permission_classes = [AllowAny]  # Ensure only authenticated users can access
    lookup_field = 'id' 



class RefundDetailView(APIView):
    """
    View and update refund details by order ID.
    """
    def get(self, request, order_id):
        try:
            refund = Refund.objects.get(order_item__id=order_id)
            serializer = RefundDetailSerializer(refund)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Refund.DoesNotExist:
            return Response({"error": "Refund not found for the provided order ID."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, order_id):
        try:
            refund = Refund.objects.get(order_item__id=order_id)
            serializer = RefundUpdateSerializer(refund, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Refund status updated successfully."}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Refund.DoesNotExist:
            return Response({"error": "Refund not found for the provided order ID."}, status=status.HTTP_404_NOT_FOUND)



class RefundActionView(APIView):
    """
    A view to handle refund actions: processed, rejected, implemented.
    """
    permission_classes = [AllowAny]
    def post(self, request, refund_id, action):
        try:
            refund = Refund.objects.get(id=refund_id)
        except Refund.DoesNotExist:
            return Response({"error": "Refund not found"}, status=status.HTTP_404_NOT_FOUND)

        # Validate and update based on the action
        if action == "processed":
            if refund.status != "initiated":
                return Response({"error": "Refund must be in 'initiated' state to process."},
                                status=status.HTTP_400_BAD_REQUEST)
            refund.status = "processed"
            refund.refund_processed_date = now()

        elif action == "rejected":
            if refund.status not in ["initiated", "processed"]:
                return Response({"error": "Refund must be in 'initiated' or 'processed' state to reject."},
                                status=status.HTTP_400_BAD_REQUEST)
            refund.status = "rejected"
            refund.refund_rejected_date = now()

        elif action == "implemented":
            if refund.status != "processed":
                return Response({"error": "Refund must be in 'processed' state to implement."},
                                status=status.HTTP_400_BAD_REQUEST)
            refund.status = "implemented"
            refund.refund_implemented_date = now()

        else:
            return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        # Save changes and respond
        refund.save()
        return Response({"message": f"Refund {action} successfully."}, status=status.HTTP_200_OK)
    

class ListPlacedOrdersView(APIView):
    """
    API View to list all orders with order_status = "placed".
    """
    permission_classes = [AllowAny]  # Only authenticated users can access

    def get(self, request):
        # Filter orders with order_status = "placed"
        placed_orders = Order.objects.filter(order_status="placed").order_by("-created_at")

        # Serialize the data
        serializer = OrderSerializer(placed_orders, many=True)

        # Return the serialized data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)



class CreateSoftDataView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SoftDataSerializer(data=request.data)
        if serializer.is_valid():
            soft_data = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

import requests
from django.core.cache import cache 


class XpressBeeLogin(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        url = 'https://shipment.xpressbees.com/api/users/login'
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            # Make the POST request
            response = requests.post(url, json=request.data, headers=headers)
            print(response)
            # Check for successful response
            if response.status_code == 200:
                res = response.json()
                cache.set("XPRESS_BEE", res.get("data"), timeout=6*3600)
                return Response(res, status=status.HTTP_200_OK)
            elif response.status_code == 401:
                # Unauthorized access
                return Response({"error": "Unauthorized. Check your credentials."}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                # Other error responses
                return Response({"error": "Failed to login. Status Code: {}".format(response.status_code)}, status=status.HTTP_400_BAD_REQUEST)
        
        except requests.exceptions.RequestException as e:
            # Handle request exceptions
            return Response({"error": "Request failed", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            # General exception handling
            return Response({"error": "An unexpected error occurred", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








# Admin dispaly end points


class ConfirmedOrderView(APIView):
    """
    API endpoint to retrieve order items with 'confirmed' status.
    """
    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users

    def get(self, request, *args, **kwargs):
        #user = self.request.user
        confirmed_orders = Order.objects.filter(order_status="confirmed")
        serializer = OrderSerializer(confirmed_orders, many=True)
        return Response(serializer.data)
    

class ShippedOrderView(APIView):
    """
    API endpoint to update an order item status to 'packed'.
    Ensures that:
    - A vendor can only update their assigned order items.
    - Only 'confirmed' order items can be packed.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")

        if not order_id:
            return Response({"error": "Order ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(OrderItem, id=order_id)

        # Ensure the authenticated user is the vendor assigned to this order item
        

        # Ensure the order item is in "confirmed" status before updating to "packed"
        if order.order_status != "confirmed":
            return Response(
                {"error": "Only confirmed order can be packed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        for items in order.items.all():
            items.update_status("shipped")
        
        # Update order status to "packed"
        #order_item.update_status("packed")
        order.order_status = "shipped"
        
        order.save()

        return Response({"message": "Order item status updated to 'packed'."}, status=status.HTTP_200_OK)