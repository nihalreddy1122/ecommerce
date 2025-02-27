# Generated by Django 5.1.4 on 2025-02-21 10:30

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('vendors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=150, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='AttributeValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=150, unique=True)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='products.attribute')),
            ],
            options={
                'unique_together': {('attribute', 'value')},
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=150, unique=True)),
                ('banners', models.ImageField(blank=True, help_text='Banner image for the category', null=True, upload_to='category_banners/')),
                ('icon', models.ImageField(blank=True, help_text='Icon image for the category', null=True, upload_to='category_icons/')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='products.category')),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, max_length=250, unique=True)),
                ('description', models.TextField(blank=True, help_text='Detailed product description', null=True)),
                ('additional_details', models.JSONField(blank=True, help_text='Structured additional details for the product', null=True)),
                ('thumbnail', models.ImageField(null=True, upload_to='product_thumbnails/')),
                ('stock', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('is_returnable', models.BooleanField(default=False, help_text='Can this product be returned?')),
                ('max_return_days', models.PositiveIntegerField(blank=True, help_text='Maximum return days (if returnable)', null=True)),
                ('is_cancelable', models.BooleanField(default=True, help_text='Can this product be canceled?')),
                ('cancellation_stage', models.CharField(blank=True, choices=[('before_packing', 'Before Packing'), ('before_shipping', 'Before Shipping'), ('before_delivery', 'Before Delivery')], help_text='Stage at which cancellation is allowed', max_length=50, null=True)),
                ('is_cod_allowed', models.BooleanField(default=True, help_text='Is cash on delivery allowed for this product?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='products.category')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='vendors.vendordetails')),
            ],
        ),
        migrations.CreateModel(
            name='FeaturedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp when the product was marked as featured')),
                ('vendor', models.ForeignKey(help_text='Vendor owning the featured product', on_delete=django.db.models.deletion.CASCADE, related_name='featured_products', to='vendors.vendordetails')),
                ('product', models.OneToOneField(help_text='The featured product', on_delete=django.db.models.deletion.CASCADE, related_name='featured_status', to='products.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='product_images/')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('offer_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stock', models.PositiveIntegerField()),
                ('sku', models.CharField(blank=True, help_text='Unique SKU for the product variant', max_length=14, unique=True)),
                ('attributes', models.ManyToManyField(related_name='variants', to='products.attributevalue')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='products.product')),
            ],
        ),
        migrations.CreateModel(
            name='VariantImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='variant_images/')),
                ('product_variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.productvariant')),
            ],
        ),
        migrations.CreateModel(
            name='LimitedEditionProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('limited_stock', models.PositiveIntegerField(help_text='Stock allocated specifically for Limited Edition')),
                ('available_from', models.DateTimeField(default=django.utils.timezone.now, help_text='Start date for Limited Edition availability')),
                ('available_until', models.DateTimeField(help_text='End date for Limited Edition availability')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('vendor', models.ForeignKey(help_text='Vendor who is setting the Limited Edition', on_delete=django.db.models.deletion.CASCADE, to='vendors.vendordetails')),
                ('product', models.OneToOneField(help_text='The product being marked as Limited Edition', on_delete=django.db.models.deletion.CASCADE, related_name='limited_edition', to='products.product')),
            ],
            options={
                'ordering': ['-available_from'],
                'constraints': [models.CheckConstraint(condition=models.Q(('available_from__lt', models.F('available_until'))), name='valid_limited_edition_dates')],
            },
        ),
    ]
