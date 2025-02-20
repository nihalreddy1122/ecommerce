from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from products.models import ProductVariant
from django.shortcuts import get_object_or_404
from ecommerce_platform import settings
from .tasks import update_payment_status

class CartView(APIView):
    """
    Retrieve the current user's cart or update it by adding/updating/removing items.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve the current user's cart.
        """
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Add a product variant to the cart or update its quantity.
        """
        cart, created = Cart.objects.get_or_create(user=request.user)
        data = request.data
        product_variant = get_object_or_404(ProductVariant, id=data.get('product_variant_id'))
        quantity = data.get('quantity', 1)

        if quantity < 1:
            return Response({"error": "Quantity must be at least 1."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the item already exists in the cart
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product_variant=product_variant)

        if not item_created:  # Item already exists, update the quantity
            cart_item.quantity += quantity
        else:  # New item added
            cart_item.quantity = quantity

        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request):
        """
        Update the quantity of an item in the cart.
        """
        cart = get_object_or_404(Cart, user=request.user)
        data = request.data
        cart_item = get_object_or_404(CartItem, id=data.get('cart_item_id'), cart=cart)
        new_quantity = data.get('quantity')

        if new_quantity is None or new_quantity < 1:
            cart_item.delete()  # Remove item if quantity is invalid or zero
            return Response({"message": "Cart item removed."}, status=status.HTTP_200_OK)

        cart_item.quantity = new_quantity
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        """
        Remove an item from the cart.
        """
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, id=request.data.get('cart_item_id'), cart=cart)
        cart_item.delete()
        return Response({"message": "Cart item removed."}, status=status.HTTP_200_OK)






from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem, Order, OrderItem, SubOrder
from .serializers import OrderSerializer
from django.db import transaction
from products.models import ProductVariant
from .models import Cart, Order, OrderItem, SubOrder
from authusers.models import Address
from authusers.serializers import AddressSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils.timezone import now
from cart_orders.models import Cart, Order, OrderItem, SubOrder, DeliveryDetail
from cart_orders.serializers import OrderSerializer, AddressSerializer
from authusers.models import Address

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils.timezone import now
from .models import Cart, CartItem, Order, OrderItem, SubOrder, DeliveryDetail
from .serializers import OrderSerializer, AddressSerializer
from authusers.models import Address

class CheckoutView(APIView):
    """
    Handles the checkout process, including stock validation, order creation,
    address handling, and managing sub-orders for vendors.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id=None):
        """
        Retrieve the user's active cart or a specific order by ID.
        """
        if order_id:
            # Retrieve a specific order by ID
            order = Order.objects.filter(customer=request.user, id=order_id).first()
            if not order:
                return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Retrieve the user's active cart
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = cart.items.all()
        cart_data = []

        for item in cart_items:
            cart_data.append({
                "product_variant": item.product_variant.id,
                "product_name": item.product_variant.product.name,
                "quantity": item.quantity,
                "price": item.product_variant.offer_price,
                "subtotal": item.get_subtotal(),
            })

        total_price = sum(item.get_subtotal() for item in cart_items)

        return Response({
            "cart_items": cart_data,
            "total_price": total_price
        }, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request):
        """
        Validates stock, creates an order, associates an address, and clears the cart upon successful checkout.
        """
        cart = Cart.objects.filter(user=request.user).first()

        if not cart or not cart.items.exists():
            return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Handle address selection or creation
        address_id = request.data.get('address_id')
        if address_id:
            address = get_object_or_404(Address, id=address_id, user=request.user)
        else:
            address_data = request.data.get('address')
            if not address_data:
                return Response({"error": "Address information is required."}, status=status.HTTP_400_BAD_REQUEST)

            address_serializer = AddressSerializer(data=address_data, context={'request': request})
            if address_serializer.is_valid():
                address = address_serializer.save()
            else:
                return Response(address_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Validate stock availability
        cart_items = cart.items.all()
        insufficient_stock_items = []

        for item in cart_items:
            if item.quantity > item.product_variant.stock:
                insufficient_stock_items.append({
                    "product_variant": item.product_variant.id,
                    "available_stock": item.product_variant.stock,
                    "requested_quantity": item.quantity
                })

        if insufficient_stock_items:
            return Response({
                "error": "Insufficient stock for some items.",
                "details": insufficient_stock_items
            }, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total price
        total_price = sum(item.get_subtotal() for item in cart_items)

        # Determine payment mode
        payment_mode = request.data.get('payment_mode', 'prepaid')
        print(f"Received payment_mode: {payment_mode}")  # Debugging log

        # Determine payment status based on payment mode
        payment_status = "cod_pending" if payment_mode.upper() == "COD" else "pending"
        print(f"Setting payment_status to: {payment_status}")  # Debugging log

        # Create the main order
        order = Order.objects.create(
            customer=request.user,
            total_price=total_price,
            payment_status=payment_status,
            address=address
        )
        print(f"Order created with payment_status: {order.payment_status}")  # Debugging log

        # Create order items and sub-orders
        vendor_subtotals = {}
        for item in cart_items:
            # Deduct stock
            product_variant = item.product_variant
            product_variant.stock -= item.quantity
            product_variant.save()

            # Create order item
            OrderItem.objects.create(
                order=order,
                product_variant=product_variant,
                quantity=item.quantity,
                price=product_variant.offer_price
            )

            # Track vendor-specific subtotals
            vendor = product_variant.product.vendor
            if vendor in vendor_subtotals:
                vendor_subtotals[vendor] += item.get_subtotal()
            else:
                vendor_subtotals[vendor] = item.get_subtotal()

        # Create sub-orders
        for vendor, subtotal in vendor_subtotals.items():
            SubOrder.objects.create(order=order, vendor=vendor, subtotal=subtotal)

        # Create delivery details
        DeliveryDetail.objects.create(
            order=order,
            address=address,
            delivery_charges=50.00,  # Example delivery charge
            platform_price=20.00,  # Example platform charge
        )

        # Clear the cart
        cart.items.all().delete()

        # Serialize and return the order
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)




############# Delivery Details 


class DeliveryDetailView(APIView):
    """
    Handles CRUD operations for delivery details.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Limit delivery details to those associated with the logged-in user."""
        return DeliveryDetail.objects.filter(order__customer=self.request.user)

    def get(self, request, pk=None):
        """Retrieve delivery details (list or single)."""
        if pk:
            try:
                delivery_detail = self.get_queryset().get(pk=pk)
            except DeliveryDetail.DoesNotExist:
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = DeliveryDetailSerializer(delivery_detail, context={"request": request})
            return Response(serializer.data)

        delivery_details = self.get_queryset()
        serializer = DeliveryDetailSerializer(delivery_details, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        """Create a delivery detail entry."""
        serializer = DeliveryDetailSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        """Update an existing delivery detail."""
        if not pk:
            return Response({"detail": "Method not allowed without specifying a resource."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        try:
            delivery_detail = self.get_queryset().get(pk=pk)
        except DeliveryDetail.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = DeliveryDetailSerializer(delivery_detail, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Cart, Order, OrderItem, DeliveryDetail
from .serializers import OrderSerializer, AddressSerializer
from authusers.models import Address

class BuyNowView(APIView):
    """
    Handles the flow for 'Buy Now': creating an order, order items, and delivery details.
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        """
        Validate stock, create an order, associate an address, and clear the cart upon successful checkout.
        """
        # Get the cart
        cart = Cart.objects.filter(user=request.user).first()

        if not cart or not cart.items.exists():
            return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Handle address selection or creation
        address_id = request.data.get('address_id')
        if address_id:
            # Use an existing address
            address = get_object_or_404(Address, id=address_id, user=request.user)
        else:
            # Create a new address
            address_data = request.data.get('address')
            if not address_data:
                return Response({"error": "Address information is required."}, status=status.HTTP_400_BAD_REQUEST)

            address_serializer = AddressSerializer(data=address_data, context={'request': request})
            if address_serializer.is_valid():
                address = address_serializer.save()
            else:
                return Response(address_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Validate stock availability
        cart_items = cart.items.all()
        insufficient_stock_items = []

        for item in cart_items:
            if item.quantity > item.product_variant.stock:
                insufficient_stock_items.append({
                    "product_variant": item.product_variant.id,
                    "available_stock": item.product_variant.stock,
                    "requested_quantity": item.quantity
                })

        if insufficient_stock_items:
            return Response(
                {"error": "Insufficient stock for some items.", "details": insufficient_stock_items},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate total price
        total_price = sum(item.get_subtotal() for item in cart_items)

        # Determine payment mode
        payment_mode = request.data.get('payment_mode', 'prepaid')
        print(f"Received payment_mode: {payment_mode}")  # Debugging

        # Determine payment status based on payment mode
        payment_status = "cod_pending" if payment_mode == "COD" else "pending"

        # Create the main order
        order = Order.objects.create(
            customer=request.user,
            total_price=total_price,
            payment_status=payment_status,
            address=address
        )
        print(f"Order created with payment_status: {order.payment_status}")  # Debugging

        # Create order items
        for item in cart_items:
            # Deduct stock
            product_variant = item.product_variant
            product_variant.stock -= item.quantity
            product_variant.save()

            # Create order item
            OrderItem.objects.create(
                order=order,
                product_variant=product_variant,
                quantity=item.quantity,
                price=product_variant.offer_price
            )

        # Create delivery details
        DeliveryDetail.objects.create(
            order=order,
            address=address,
            delivery_charges=50.00,  # Example delivery charge
            platform_price=20.00,  # Example platform charge
        )

        # Clear the cart
        cart.items.all().delete()

        # Serialize the order
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


from authusers.models import Address
from authusers.serializers import AddressSerializer
from rest_framework import generics, permissions
from rest_framework.views import APIView

class UserAddressListView(APIView):
    """
    API endpoint to fetch all addresses of the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        addresses = Address.objects.filter(user=user)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

import razorpay


class PaymentInitializationView(APIView):
    """
    Generates Razorpay payment order_id for a given order.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Extract `order_id` from request
            order_id = request.data.get("order_id")
            if not order_id:
                return Response({"error": "Order ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the order
            order = get_object_or_404(Order, id=order_id, customer=request.user)

            # Ensure the order is still pending payment
            if order.payment_status != "pending":
                return Response({"error": "Payment is already completed or invalid for this order."}, status=status.HTTP_400_BAD_REQUEST)

            # Razorpay client initialization
            razorpay_client = razorpay.Client(auth=("rzp_test_EVswR8OHh71h2F", "PY7vpZUFrdPBupe01k8fJb7F"))

            # Generate payment order
            amount = int(order.total_price * 100)  # Convert to paise
            payment_order = razorpay_client.order.create(
                {
                    "amount": amount,
                    "currency": "INR",
                    "receipt": f"order_{order.id}",
                    "payment_capture": 1,  # Auto-capture enabled
                }
            )
            order.payment_status = "Paid"
            order.razorpay_order_id = payment_order["id"]
            print(order)
            order.save()

            # Return Razorpay details to the frontend
            return Response(
                {
                    "razorpay_order_id": payment_order["id"],
                    "amount": payment_order["amount"],
                    "currency": payment_order["currency"],
                    "key": "rzp_test_EVswR8OHh71h2F",  # Provide the Razorpay API Key for frontend
                },
                status=status.HTTP_200_OK,
            )

        except razorpay.errors.BadRequestError as e:

            order_id = request.data.get("order_id")
            if not order_id:
                return Response({"error": "Order ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the order
            order = get_object_or_404(Order, id=order_id, customer=request.user)
            print(order)

            return Response({"error": "Razorpay BadRequestError", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Handle unexpected errors
            return Response({"error": "An unexpected error occurred.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.template.loader import render_to_string
from django.core.mail import send_mail
from celery import shared_task
from cart_orders.tasks import send_order_placed_email

class PaymentVerificationView(APIView):
    """
    Verifies Razorpay payment and updates the order status.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Extract payment details
        order_id = request.data.get("order_id")
        razorpay_order_id = request.data.get("razorpay_order_id")
        payment_id = request.data.get("razorpay_payment_id")
        signature = request.data.get("razorpay_signature")

        if not all([order_id, payment_id, signature]):
            return Response({"error": "Incomplete payment details provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the order
        order = get_object_or_404(Order, id=order_id, customer=request.user)

        # Verify the Razorpay payment signature
        razorpay_client = razorpay.Client(auth=("rzp_test_EVswR8OHh71h2F", "PY7vpZUFrdPBupe01k8fJb7F"))
        try:
            razorpay_client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": payment_id,
                    "razorpay_signature": signature,
                }
            )
            # Update the order's payment status
            order.payment_status = "paid"
            order.save()

            # Update payment status for related order items
            update_payment_status(order_id)

            # Trigger the email task
            send_order_placed_email.delay(order.id)

        except razorpay.errors.SignatureVerificationError:
            return Response({"error": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Payment verified successfully."}, status=status.HTTP_200_OK)



class OrderItemListView(APIView):
    """
    View to list all order items for a specific order.
    """
    permission_classes = [IsAuthenticated]  # Only authenticated users can access

    def get(self, request, order_id):
        # Get the order by ID and ensure it belongs to the requesting user
        order = get_object_or_404(Order, id=order_id, customer=request.user)

        # Fetch all items related to this order
        order_items = order.items.all()

        # Serialize the order items
        serializer = OrderItemSerializer(order_items, many=True)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from cart_orders.models import Order
import razorpay
from django.conf import settings

class RetryPaymentView(APIView):
    """
    Handles payment retries for failed or pending orders.
    """

    def post(self, request, *args, **kwargs):
        try:
            # Fetch the order ID and callback URL from the request
            order_id = request.data.get("order_id")
            callback_url = request.data.get("callback_url")

            if not order_id:
                return Response({"error": "Order ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            if not callback_url:
                return Response({"error": "Callback URL is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the order
            order = Order.objects.get(id=order_id)

            # Check if the payment status allows retry
            if order.payment_status not in ['failed', 'pending']:
                return Response({"error": "Payment cannot be retried for this order."}, status=status.HTTP_400_BAD_REQUEST)

            # Razorpay client setup
            razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Create a new payment link for the existing order
            payment_link = razorpay_client.payment_link.create({
                "amount": int(order.total_price * 100),  # Convert to paise
                "currency": "INR",
                "description": f"Retry payment for Order #{order.id}",
                "callback_url": callback_url,  # Use the callback URL from the request
                "callback_method": "get"
            })

            # Update the order status
            order.payment_status = "retrying"
            order.save()

            return Response({
                "message": "Payment link generated successfully.",
                "payment_link": payment_link['short_url']
            }, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        except razorpay.errors.RazorpayError as e:
            return Response({"error": f"Razorpay Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Internal Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



























from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from cart_orders.models import OrderItem


def generate_shipping_label(request, order_item_id):
    """
    Generate a shipping label for a specific order item.
    """
    try:
        # Fetch the order item using the provided order_item_id
        order_item = OrderItem.objects.get(id=order_item_id, payment_status='paid')

        # Extract details
        customer_details = {
            "name": f"{order_item.order.customer.first_name} {order_item.order.customer.last_name}",
            "email": order_item.order.customer.email,
            "phone_number": order_item.order.customer.phone_number
        }

        delivery_address = {
            "full_name": order_item.order.delivery_detail.address.full_name,
            "address_line_1": order_item.order.delivery_detail.address.address_line_1,
            "address_line_2": order_item.order.delivery_detail.address.address_line_2,
            "city": order_item.order.delivery_detail.address.city,
            "state": order_item.order.delivery_detail.address.state,
            "postal_code": order_item.order.delivery_detail.address.postal_code,
            "country": order_item.order.delivery_detail.address.country
        }

        product_variant = order_item.product_variant

    except OrderItem.DoesNotExist:
        return HttpResponse("Order item not found or payment not completed.", status=404)

    # Create an HTTP response with a PDF mimetype
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="shipping_label_{order_item_id}.pdf"'

    # Initialize ReportLab canvas
    c = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Draw sections as per the second image template
    c.setFont("Helvetica-Bold", 12)

    # Ship to Section
    c.drawString(40, height - 50, "SHIP TO:")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 70, delivery_address["full_name"])
    c.drawString(40, height - 90, delivery_address["address_line_1"])
    if delivery_address["address_line_2"]:
        c.drawString(40, height - 110, delivery_address["address_line_2"])
    c.drawString(40, height - 130, f"{delivery_address['city']}, {delivery_address['state']}")
    c.drawString(40, height - 150, f"{delivery_address['postal_code']}, {delivery_address['country']}")

    # From Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(300, height - 50, "FROM:")
    c.setFont("Helvetica", 10)
    c.drawString(300, height - 70, "ACME Corporation")
    c.drawString(300, height - 90, "456 Industrial Blvd")
    c.drawString(300, height - 110, "Los Angeles, 90001, USA")

    # Order Details Section
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, height - 180, "ORDER DETAILS:")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 200, f"Order ID: {order_item.id}")
    c.drawString(40, height - 220, f"Weight: 2.5 KG")  # Replace with dynamic weight if available
    c.drawString(40, height - 240, "Dimensions: 12cm x 12cm x 12cm")  # Replace with dynamic dimensions
    c.drawString(40, height - 260, f"Shipping Date: {order_item.updated_at.strftime('%Y-%m-%d')}")

    # Remarks Section
    c.setFont("Helvetica-Bold", 10)
    c.drawString(300, height - 180, "REMARKS:")
    c.setFont("Helvetica", 10)
    c.drawString(300, height - 200, "NO REMARKS")

    # Barcode Section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 300, "TRACKING NO:")
    c.drawString(150, height - 300, f"TRACK{order_item.id}US")
    c.drawString(40, height - 340, "-----------------------------------------")
    c.drawString(40, height - 360, f"TRACK{order_item.id}US")

    # Save the PDF
    c.save()
    return response

import hmac
import hashlib
import json
from django.http import JsonResponse, HttpResponseBadRequest
from ecommerce_platform.settings import RAZORPAY_WEBHOOK_SECRET
from rest_framework.permissions import AllowAny

class RazorpayWebhookView(APIView):
    permission_classes = [AllowAny] 
    def get(self, request, *args, **kwargs):
        return HttpResponse("Razorpay webhook received")
    def post(self, request, *args, **kwargs):
        # Get the webhook payload and signature from the headers
        payload = request.body
        received_signature = request.headers.get('X-Razorpay-Signature')

        # Verify the signature
        generated_signature = hmac.new(
            bytes(RAZORPAY_WEBHOOK_SECRET, 'utf-8'),
            msg=payload,
            digestmod=hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(received_signature, generated_signature):
            return HttpResponseBadRequest("Invalid webhook signature")

        # Parse the payload
        event = json.loads(payload)
        event_type = event.get("event")

        # Handle different event types
# Handle different event types
        if event_type == "payment.captured":
            razorpay_order_id = event["payload"]["payment"]["entity"]["order_id"]  # Razorpay Order ID
            payment_id = event["payload"]["payment"]["entity"]["id"]

            # Update the payment status of the order
            try:
                # Match using razorpay_order_id instead of local order_id
                order = Order.objects.get(razorpay_order_id=razorpay_order_id)
                order.payment_status = "paid"
                order.transaction_id = payment_id
                update_payment_status(razorpay_order_id)
                order.save()
            except Order.DoesNotExist:
                return JsonResponse({"error": "Order not found"}, status=404)

        elif event_type == "payment.failed":
            razorpay_order_id = event["payload"]["payment"]["entity"]["order_id"]  # Razorpay Order ID
            payment_id = event["payload"]["payment"]["entity"]["id"]

            # Update the order status to "failed"
            try:
                order = Order.objects.get(razorpay_order_id=razorpay_order_id)
                order.payment_status = "failed"
                order.transaction_id = payment_id
                order.save()
            except Order.DoesNotExist:
                return JsonResponse({"error": "Order not found"}, status=404)

        # Return success response
        return JsonResponse({"status": "success"}, status=200)
    

    