# Generated by Django 5.1.4 on 2025-01-24 08:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cart_orders', '0001_initial'),
        ('products', '0001_initial'),
        ('vendors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PriceRangeCommission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_price', models.DecimalField(decimal_places=2, help_text='Minimum price of the range', max_digits=10)),
                ('max_price', models.DecimalField(blank=True, decimal_places=2, help_text='Maximum price of the range (leave blank for no upper limit)', max_digits=10, null=True)),
                ('commission_rate', models.DecimalField(decimal_places=2, help_text='Commission rate for this price range (in percentage)', max_digits=5)),
                ('platform_charges', models.DecimalField(decimal_places=2, default=0.0, help_text='Platform charges as a fixed amount for this price range', max_digits=10)),
            ],
            options={
                'verbose_name': 'Price Range Commission',
                'verbose_name_plural': 'Price Range Commissions',
            },
        ),
        migrations.CreateModel(
            name='CommissionAndGST',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_price', models.DecimalField(decimal_places=2, help_text='Price of the product (inclusive of GST)', max_digits=10)),
                ('commission_rate', models.DecimalField(decimal_places=2, help_text='Commission rate applied to this product', max_digits=5)),
                ('commission_amount', models.DecimalField(decimal_places=2, help_text='Commission amount deducted based on the rate', max_digits=10)),
                ('gst_on_commission', models.DecimalField(decimal_places=2, help_text='GST applied on the commission amount', max_digits=10)),
                ('platform_charges', models.DecimalField(decimal_places=2, help_text='Platform charges for this product', max_digits=10)),
                ('total_deduction', models.DecimalField(decimal_places=2, help_text='Total deductions (commission + GST + platform charges)', max_digits=10)),
                ('vendor_earnings', models.DecimalField(decimal_places=2, help_text='Final earnings for the vendor after all deductions', max_digits=10)),
                ('calculated_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp when the calculation was performed')),
                ('order_item', models.OneToOneField(help_text='The specific order item linked to these commission details', on_delete=django.db.models.deletion.CASCADE, related_name='commission_details', to='cart_orders.orderitem')),
                ('product', models.ForeignKey(help_text='The product for which these details are calculated', on_delete=django.db.models.deletion.CASCADE, related_name='commission_details', to='products.product')),
                ('vendor', models.ForeignKey(help_text='The vendor who owns the product', on_delete=django.db.models.deletion.CASCADE, related_name='commission_details', to='vendors.vendordetails')),
            ],
        ),
    ]
