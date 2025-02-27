# Generated by Django 5.1.4 on 2025-02-21 16:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_portal', '0003_initial'),
        ('cart_orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WareHouseAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=15)),
                ('address_line_1', models.CharField(max_length=255)),
                ('address_line_2', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('postal_code', models.CharField(max_length=10)),
                ('country', models.CharField(default='India', max_length=100)),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='XpressBeeShipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('xpressbees_awb_number', models.CharField(blank=True, help_text='Xpressbees AWB number', max_length=50, null=True)),
                ('status', models.CharField(default='pending', help_text='Shipment status', max_length=50)),
                ('package_weight', models.FloatField()),
                ('package_length', models.FloatField()),
                ('package_breadth', models.FloatField()),
                ('package_height', models.FloatField()),
                ('payment_type', models.CharField(choices=[('cod', 'Cash on Delivery'), ('prepaid', 'Prepaid'), ('reverse', 'Reverse')], max_length=10)),
                ('shipping_charges', models.FloatField(blank=True, default=0, null=True)),
                ('discount', models.FloatField(blank=True, default=0, null=True)),
                ('cod_charges', models.FloatField(blank=True, default=0, null=True)),
                ('order_amount', models.FloatField(blank=True, default=0, null=True)),
                ('collectable_amount', models.FloatField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='xpress_bees', to='cart_orders.order')),
            ],
        ),
    ]
