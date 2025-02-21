from django.db import models
from django.conf import settings
from products.models import ProductVariant
from django.utils.timezone import now
from vendors.models import VendorDetails
from authusers.models import Address
from decimal import Decimal

class Cart(models.Model):
    """
    Represents a shopping cart for a specific user.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        help_text="The user associated with this cart."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="The date and time when the cart was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="The date and time when the cart was last updated.")
    last_reminder_sent = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="The date and time when the last reminder email was sent."
    )


    def __str__(self):
        return f"Cart for {self.user.email}"


class CartItem(models.Model):
    """
    Represents an individual item in a cart.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        help_text="The cart this item belongs to."
    )
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="cart_items",
        help_text="The specific product variant added to the cart."
    )
    quantity = models.PositiveIntegerField(
        default=1, 
        help_text="The quantity of this product in the cart."
    )
    added_at = models.DateTimeField(
        auto_now_add=True, 
        help_text="The date and time when the item was added to the cart."
    )

    # Override save method to update Cart's updated_at field when a CartItem is changed
    def save(self, *args, **kwargs):
        """
        Override save to update the cart's updated_at field whenever a cart item is modified.
        """
        super().save(*args, **kwargs)
        self.cart.updated_at = now()
        self.cart.save(update_fields=["updated_at"])  # Update only the updated_at field

    def __str__(self):
        return f"{self.quantity} x {self.product_variant.product.name}"

    def get_subtotal(self):
        """
        Calculate the subtotal for this item (offer_price * quantity).
        """
        return self.product_variant.offer_price * self.quantity





class Order(models.Model):
    """
    Represents an order placed by a customer.
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cod_pending', 'COD Pending'),
        ('cod_paid', 'COD Paid'),
        ('cancelled', 'Cancelled'),
    ]

    ORDER_STATUS_CHOICES = [
        ('created', 'Created'),
        ('placed', 'Order Placed'),      
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        help_text="The customer who placed the order."
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        help_text="The address used for this order."
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Total price of the order."
    )
    payment_status = models.CharField(
        max_length=15,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        help_text="Payment status for the order."
    )
    order_status = models.CharField(
        max_length=15,
        choices=ORDER_STATUS_CHOICES,
        default='created',
        help_text="Current status of the order."
    )
    cod_remittance_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when COD payment was remitted."
    )
    cod_payment_received = models.BooleanField(
        default=False,
        help_text="Indicates whether COD payment has been received."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the order was created")  # Track order creation time
    updated_at = models.DateTimeField(auto_now=True)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.email}"




from django.db import models
from django.utils.timezone import now

class OrderItem(models.Model):
    """
    Represents an individual item in an order.
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    
    ORDER_STATUS_CHOICES = [
        ('created', 'Created'),
        ('confirmed', 'Confirmed'),
        ('packed', 'Packed'),
        ('warehouse', 'Warehouse'),
        ("shipped", 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        help_text="The order this item belongs to."
    )
    product_variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="order_items",
        help_text="The specific product variant purchased."
    )
    quantity = models.PositiveIntegerField(help_text="The quantity of this product purchased.")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price of the product at the time of purchase.")
    vendor = models.ForeignKey(
        VendorDetails,
        on_delete=models.CASCADE,
        related_name="order_items",
        help_text="The vendor associated with this product.",
        null=True,
        blank=True,
    )
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        help_text="Payment status for the order."
    )
    order_status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='confirmed',
        help_text="Status of the order item."
    )

    # Timestamp fields for each order status (default to NULL)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    packed_at = models.DateTimeField(null=True, blank=True)
    warehouse_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, help_text="The date and time when this item was added to the order.")
    updated_at = models.DateTimeField(auto_now=True, help_text="The date and time when this item was last updated.")
    delivery_date = models.DateTimeField(null=True, blank=True)  # Allow NULL values

    def save(self, *args, **kwargs):
        """
        Automatically set the vendor based on the product variant's product.
        Calculates and updates commission details for the order item.
        """
        if not self.vendor:
            self.vendor = self.product_variant.product.vendor

        super().save(*args, **kwargs)  # Save the OrderItem instance first

        # ---------------- NEW UPDATE: Commission and GST Calculation ----------------
        from commission_and_calculations.models import CommissionAndGST
        from commission_and_calculations.calculations import calculate_commission_and_gst

        # Fetch product price from the linked ProductVariant
        product_price = self.product_variant.offer_price

        # Call the utility function to calculate commission details
        calculations = calculate_commission_and_gst(product_price)

        # Create or update the CommissionAndGST record
        CommissionAndGST.objects.update_or_create(
            order_item=self,
            defaults={
                "product": self.product_variant.product,
                "vendor": self.vendor,
                "product_price": product_price,
                "commission_rate": calculations["commission_rate"],
                "commission_amount": calculations["commission_amount"],
                "gst_on_commission": calculations["gst_on_commission"],
                "platform_charges": calculations["platform_charges"],
                "total_deduction": calculations["total_deduction"],
                "vendor_earnings": calculations["vendor_earnings"],
            }
        )

    def update_status(self, new_status):
        """
        Updates the status of the order item with validation for allowed transitions.
        Automatically sets the timestamp for the new status.
        """
        valid_transitions = {
            'confirmed': ['packed'],
            'packed': ['warehouse'],
            'warehouse': ['shipped'],
            'shipped': ['delivered'],
            'delivered': [],
            'cancelled': [],
            'returned': [],
        }

        if new_status in valid_transitions.get(self.order_status, []):
            self.order_status = new_status

            # Set the corresponding timestamp
            if new_status == "confirmed":
                self.confirmed_at = now()
            elif new_status == "packed":
                self.packed_at = now()
            elif new_status == "warehouse":
                self.warehouse_at = now()
            elif new_status == "shipped":
                self.shipped_at = now()
            elif new_status == "delivered":
                self.delivered_at = now()
            elif new_status == "cancelled":
                self.cancelled_at = now()
            elif new_status == "returned":
                self.returned_at = now()

            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.quantity} x {self.product_variant.product.name} in Order #{self.order.id}"





class SubOrder(models.Model):
    """
    Represents a sub-order for vendor-specific products in a multi-vendor order.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="sub_orders",
        help_text="The main order this sub-order belongs to."
    )
    vendor = models.ForeignKey(
        VendorDetails,
        on_delete=models.CASCADE,
        related_name="sub_orders",
        help_text="The vendor associated with this sub-order."
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, help_text="Subtotal for the vendor-specific items.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SubOrder #{self.id} for {self.vendor.user.email} (Order #{self.order.id})"


from django.utils.timezone import now
from decimal import Decimal
from datetime import timedelta

class DeliveryDetail(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="delivery_detail")
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name="delivery_details")
    expected_delivery_date = models.DateField()
    delivery_charges = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    platform_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    overall_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set on creation

    def save(self, *args, **kwargs):
        """
        Calculate the overall price dynamically before saving.
        """
        if not self.expected_delivery_date:
            self.expected_delivery_date = now().date() + timedelta(days=7)

        # Ensure all values are Decimal
        self.delivery_charges = Decimal(self.delivery_charges)
        self.platform_price = Decimal(self.platform_price)
        self.overall_price = Decimal(self.order.total_price) + self.delivery_charges + self.platform_price
        super().save(*args, **kwargs)
