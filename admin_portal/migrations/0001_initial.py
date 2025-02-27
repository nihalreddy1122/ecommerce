# Generated by Django 5.1.4 on 2025-02-21 10:31

import admin_portal.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(help_text='Description of the action performed', max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True, help_text='When the action was performed')),
            ],
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, help_text='Refund amount for the order item.', max_digits=10)),
                ('status', models.CharField(choices=[('initiated', 'Refund Initiated'), ('processed', 'Refund Processed'), ('rejected', 'Refund Rejected'), ('implemented', 'Refund Implemented')], default='initiated', help_text='Current status of the refund.', max_length=20)),
                ('reason', models.TextField(default='__________', help_text='Reason provided by the customer for the refund.')),
                ('refund_initiated_date', models.DateTimeField(blank=True, help_text='The date when the refund was initiated.', null=True)),
                ('refund_processed_date', models.DateTimeField(blank=True, help_text='The date when the refund was processed.', null=True)),
                ('refund_rejected_date', models.DateTimeField(blank=True, help_text='The date when the refund was rejected.', null=True)),
                ('refund_implemented_date', models.DateTimeField(blank=True, help_text='The date when the refund was implemented.', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date when the refund was created.')),
            ],
        ),
        migrations.CreateModel(
            name='RefundMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media', models.FileField(help_text='Image or video file supporting the refund request', upload_to=admin_portal.models.refund_media_upload_path)),
            ],
        ),
        migrations.CreateModel(
            name='SoftData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_address', models.TextField(help_text='Pickup address provided by admin')),
                ('shipping_address', models.TextField(help_text='Fetched from the order')),
                ('tracking_id', models.CharField(blank=True, help_text='Tracking ID from Delhivery', max_length=100, null=True)),
                ('payment_status', models.CharField(choices=[('unpaid', 'Unpaid'), ('paid', 'Paid')], default='unpaid', help_text='Payment status for the order', max_length=20)),
                ('weight', models.DecimalField(decimal_places=2, help_text='Weight of the order in kilograms', max_digits=6)),
                ('dimensions', models.JSONField(help_text='Dimensions of the order (length, breadth, height) in cm')),
                ('serviceability_checked', models.BooleanField(default=False, help_text='Indicates if serviceability check is done')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='VendorPayout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, help_text='Payout amount', max_digits=10)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processed', 'Processed')], default='pending', help_text='Status of the payout', max_length=20)),
                ('processed_at', models.DateTimeField(blank=True, help_text='When the payout was processed', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When the payout was created')),
            ],
        ),
    ]
