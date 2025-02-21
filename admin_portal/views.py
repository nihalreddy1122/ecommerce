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
from rest_framework.viewsets import ModelViewSet

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
    

class WareHouseAddressListCreateView(APIView):
    """
    API endpoint to list all warehouse addresses or create a new one.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = WareHouseAddress.objects.all()
        serializer = WareHouseAddressSerializer(addresses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = WareHouseAddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WareHouseAddressDetailView(APIView):
    """
    API endpoint to retrieve, update, or delete a specific warehouse address.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        address = get_object_or_404(WareHouseAddress, pk=pk)
        serializer = WareHouseAddressSerializer(address)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        address = get_object_or_404(WareHouseAddress, pk=pk)
        serializer = WareHouseAddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        address = get_object_or_404(WareHouseAddress, pk=pk)
        address.delete()
        return Response({"message": "Address deleted successfully."}, status=status.HTTP_204_NO_CONTENT)





class CreateReturnShipment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refund_id = request.data.get("refund_id")
        if not refund_id:
            return Response({"error": "Refund ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the refund and its associated order item
        try:
            refund = Refund.objects.get(id=refund_id, status="requested")
            order_item = refund.order_item  # Refund is linked to a single OrderItem
            order = order_item.order  # Get the associated Order
        except Refund.DoesNotExist:
            return Response({"error": "Valid refund request not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the order has an address (customer's pickup address)
        if not order.address:
            return Response({"error": "Order address not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch default warehouse (consignee/delivery address)
        warehouse = WareHouseAddress.objects.filter(is_default=True).first()
        if not warehouse:
            return Response({"error": "Default warehouse not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare the order item payload (single item return)
        order_item_payload = {
            "name": order_item.product_variant.product.name,
            "qty": order_item.quantity,
            "price": str(order_item.price),
            "sku": "555555",  # SKU placeholder (use actual SKU if available)
        }

        # Build payload for return shipment
        payload = {
            "order_number": f"#{order.id}-RET",
            "payment_type": "reverse",
            "package_weight": order_item.package_weight,
            "package_length": order_item.package_length,
            "package_breadth": order_item.package_breadth,
            "package_height": order_item.package_height,
            "request_auto_pickup": "yes",

            # Pickup from customer's address (where the product is being returned from)
            "pickup": {
                "name": order.address.full_name,
                "address": order.address.address_line_1,
                "address_2": order.address.address_line_2,
                "city": order.address.city,
                "state": order.address.state,
                "pincode": order.address.postal_code,
                "phone": order.address.phone_number,
            },

            # Deliver to warehouse (where the returned product is being sent)
            "consignee": {
                "warehouse_name": "Default Warehouse",
                "name": warehouse.full_name,
                "address": warehouse.address_line_1,
                "city": warehouse.city,
                "state": warehouse.state,
                "pincode": warehouse.postal_code,
                "phone": warehouse.phone_number,
            },

            "order_items": [order_item_payload],  # Single order item for return
            "courier_id": 1,
            "collectable_amount": 0,  # No amount collected for return
        }

        # Get Xpressbees token
        token = cache.get("XPRESS_BEE")
        if not token:
            return Response({"error": "Xpressbees login expired"}, status=status.HTTP_401_UNAUTHORIZED)

        # Send request to Xpressbees API
        url = "https://shipment.xpressbees.com/api/shipments2"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to create return shipment", "details": response.json()}, status=response.status_code)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class CreateXpressBeeShipment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data)
        print(Order.objects.filter(id=80).exists())
        print(WareHouseAddress.objects.filter(is_default=True).exists())

        warehouse = WareHouseAddress.objects.get(id=1)  # Ensure the warehouse exists
        print(warehouse.postal_code)

        # Fetch the order instance
        try:
            order = Order.objects.get(id=request.data["order_id"])  # Fetch a single instance
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Assign the primary key of the order to the request data
        request.data["order"] = order.id

        serializer = XpressBeeShipmentSerializer(data=request.data)

        print(serializer.is_valid())
        print(serializer.errors)
        
        token = cache.get("XPRESS_BEE")
        
        if not token:
            return Response(" Xpress Bees Login Expired",   status=status.HTTP_401_UNAUTHORIZED)
        if serializer.is_valid():
            shipment = serializer.save()
            order_items_payload = [
                {
                    "name": item.product_variant.product.name,
                    "qty": item.quantity,
                    "price": str(item.price),  # Convert Decimal to string
                    "sku": 555555  # Assuming the `ProductVariant` model has an SKU field
                }
                for item in order.items.all()
            ]
            # Build payload for Xpressbees API (rest of the logic remains unchanged)
            payload = {
                "order_number": f"#{shipment.order.id}",
                "shipping_charges": float(shipment.shipping_charges),
                "discount": float(shipment.discount),
                "cod_charges": float(shipment.cod_charges),
                "payment_type": shipment.payment_type,
                "order_amount": float(shipment.order_amount),
                "package_weight": shipment.package_weight,
                "package_length": shipment.package_length,
                "package_breadth": shipment.package_breadth,
                "package_height": shipment.package_height,
                "request_auto_pickup": "yes",
                "consignee": {
                    "name": shipment.order.address.full_name,
                    "address": shipment.order.address.address_line_1,
                    "address_2": shipment.order.address.address_line_2,
                    "city": shipment.order.address.city,
                    "state": shipment.order.address.state,
                    "pincode": 500061,
                    "phone": shipment.order.address.phone_number,
                },
                "pickup": {
                    "warehouse_name": "Default Warehouse",
                    "name": warehouse.full_name,
                    "address": warehouse.address_line_1,
                    "city": warehouse.city,
                    "state": warehouse.state,
                    "pincode": warehouse.postal_code,
                    "phone": warehouse.phone_number,
                },
                "order_items": order_items_payload,
                "courier_id": 1,
                "collectable_amount": float(shipment.collectable_amount),
            }
            


            # Send the payload to Xpressbees API
            url = "https://shipment.xpressbees.com/api/shipments2"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            try:
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    response_data = response.json()
                    shipment.xpressbees_awb_number = response_data.get("awb_number")
                    shipment.status = "booked"
                    shipment.save()
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"error": "Failed to create shipment", "details": response.json()},
                        status=response.status_code,
                    )
            except requests.RequestException as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


