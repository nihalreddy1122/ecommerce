from django.apps import apps
from django.db.models import Q

def calculate_commission_and_gst(product_price):
    """
    Calculate commission, GST, and vendor earnings based on dynamic price ranges,
    including handling open-ended price ranges.
    """
    # Fetch the PriceRangeCommission model dynamically
    PriceRangeCommission = apps.get_model('commission_and_calculations', 'PriceRangeCommission')

    # Fetch the applicable price range
    price_range = PriceRangeCommission.objects.filter(
        Q(min_price__lte=product_price),
        Q(max_price__gte=product_price) | Q(max_price__isnull=True)
    ).first()

    if not price_range:
        raise ValueError("No price range found for the given product price.")

    # Extract values
    commission_rate = price_range.commission_rate
    platform_charges = price_range.platform_charges

    # Calculate commission amount
    commission_amount = (product_price * commission_rate) / 100

    # Calculate GST on commission (18% of commission)
    gst_on_commission = (commission_amount * 18) / 100

    # Total commission including GST
    total_commission_with_gst = commission_amount + gst_on_commission

    # Total deductions (commission + GST + platform charges)
    total_deduction = total_commission_with_gst + platform_charges

    # Vendor earnings after all deductions
    vendor_earnings = product_price - total_deduction

    return {
        "commission_rate": commission_rate,
        "platform_charges": platform_charges,
        "commission_amount": commission_amount,
        "gst_on_commission": gst_on_commission,
        "total_commission_with_gst": total_commission_with_gst,
        "total_deduction": total_deduction,
        "vendor_earnings": vendor_earnings,
    }
