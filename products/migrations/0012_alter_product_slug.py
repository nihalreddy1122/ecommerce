# Generated by Django 5.1.4 on 2025-02-11 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_alter_productvariant_stock_delete_productvariantsize'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(blank=True, max_length=250),
        ),
    ]
