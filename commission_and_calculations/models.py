from django.db import models
from cart_orders.models import OrderItem
from products.models import Product
from vendors.models import VendorDetails
from .calculations import calculate_commission_and_gst

class PriceRangeCommission(models.Model):
    min_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Minimum price of the range")
    max_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum price of the range (leave blank for no upper limit)"
    )
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Commission rate for this price range (in percentage)")
    platform_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Platform charges as a fixed amount for this price range"
    )

    class Meta:
        verbose_name = "Price Range Commission"
        verbose_name_plural = "Price Range Commissions"

    def __str__(self):
        if self.max_price:
            return f"{self.min_price} - {self.max_price}: {self.commission_rate}% Commission + ₹{self.platform_charges} Platform Charges"
        return f"{self.min_price} and above: {self.commission_rate}% Commission + ₹{self.platform_charges} Platform Charges"



class CommissionAndGST(models.Model):
    order_item = models.OneToOneField(
        OrderItem, on_delete=models.CASCADE, related_name="commission_details",
        help_text="The specific order item linked to these commission details"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="commission_details",
        help_text="The product for which these details are calculated"
    )
    vendor = models.ForeignKey(
        VendorDetails, on_delete=models.CASCADE, related_name="commission_details",
        help_text="The vendor who owns the product"
    )
    product_price = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Price of the product (inclusive of GST)"
    )
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Commission rate applied to this product"
    )
    commission_amount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Commission amount deducted based on the rate"
    )
    gst_on_commission = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="GST applied on the commission amount"
    )
    platform_charges = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Platform charges for this product"
    )
    total_deduction = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Total deductions (commission + GST + platform charges)"
    )
    vendor_earnings = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Final earnings for the vendor after all deductions"
    )
    calculated_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the calculation was performed")

    def __str__(self):
        return f"Commission and GST for {self.product.name} - OrderItem {self.order_item.id}"

    def save(self, *args, **kwargs):
        """
        Override save method to dynamically calculate commission, GST, platform charges, and vendor earnings.
        """
        # Fetch the product price
        product_price = self.order_item.product_variant.offer_price

        # Call the utility function to perform calculations
        calculations = calculate_commission_and_gst(product_price)

        # Populate fields with calculated values
        self.product_price = product_price
        self.commission_rate = calculations["commission_rate"]
        self.commission_amount = calculations["commission_amount"]
        self.gst_on_commission = calculations["gst_on_commission"]
        self.platform_charges = calculations["platform_charges"]
        self.total_deduction = calculations["total_deduction"]
        self.vendor_earnings = calculations["vendor_earnings"]

        super().save(*args, **kwargs)  # Save the instance