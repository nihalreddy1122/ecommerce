# Generated by Django 5.1.4 on 2025-01-30 13:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_product_additional_details_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='thumbnail',
            field=models.ImageField(null=True, upload_to='product_thumbnails/'),
        ),
    ]
