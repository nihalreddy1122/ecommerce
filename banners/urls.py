from django.urls import path
from .views import *

urlpatterns = [

    path('banners/', BannerListCreateView.as_view(), name='banner-list-create'),
    path('banners/<int:pk>/', BannerDetailView.as_view(), name='banner-detail'),
    path('customer-banners/', CustomerBannerListView.as_view(), name='customer-banner-list'),

    
]
