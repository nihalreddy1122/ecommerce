from django.contrib import admin
from .models import Banner

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'banner_type', 'position', 'priority', 'is_active', 'created_at')
    list_filter = ('banner_type', 'position', 'is_active')
    search_fields = ('title', 'description')
    ordering = ('-priority', 'created_at')
    readonly_fields = ('created_at', 'updated_at')