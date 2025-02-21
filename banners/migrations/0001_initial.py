# Generated by Django 5.1.4 on 2025-02-21 10:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        ('vendors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Title of the banner', max_length=255)),
                ('description', models.TextField(blank=True, help_text='Optional description for the banner', null=True)),
                ('image', models.ImageField(help_text='Image for the banner', null=True, upload_to='banners/')),
                ('banner_type', models.CharField(choices=[('hero', 'Hero'), ('grid', 'Grid'), ('scroll', 'scroll')], default='hero', help_text='Type of the banner (Hero, Grid, scrollbar)', max_length=10)),
                ('external_url', models.URLField(blank=True, help_text='Custom external URL for the banner', null=True)),
                ('position', models.CharField(choices=[('top', 'Top'), ('middle', 'Middle'), ('scroll', 'Scroll')], default='top', help_text='Position of the banner on the page', max_length=20)),
                ('priority', models.PositiveIntegerField(default=0, help_text='Display priority for ordering banners')),
                ('is_active', models.BooleanField(default=True, help_text='Indicates if the banner is active')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When the banner was created')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='When the banner was last updated')),
                ('category', models.ForeignKey(blank=True, help_text='Optional category linked to this banner', null=True, on_delete=django.db.models.deletion.CASCADE, to='products.category')),
                ('store', models.ForeignKey(blank=True, help_text='Optional store linked to this banner', null=True, on_delete=django.db.models.deletion.CASCADE, to='vendors.vendordetails')),
            ],
            options={
                'ordering': ['-priority', 'created_at'],
            },
        ),
    ]
