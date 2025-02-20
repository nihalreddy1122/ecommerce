from django.urls import path
from .views import PriceRangeCommissionListCreateView, PriceRangeCommissionDetailView

urlpatterns = [
    path('price-ranges/', PriceRangeCommissionListCreateView.as_view(), name='price-range-list-create'),
    path('price-ranges/<int:pk>/', PriceRangeCommissionDetailView.as_view(), name='price-range-detail'),
]
