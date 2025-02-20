from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authusers.urls')),  
    path('vendor/', include('vendors.urls')),
    path('products/', include('products.urls')),
    path('banners/', include('banners.urls')),
    path('customers/', include('customer.urls')),
    path('cartorders/', include('cart_orders.urls')),
    path('admin_portal/', include('admin_portal.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)