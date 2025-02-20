from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Banner
from .serializers import BannerSerializer

class BannerPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

class BannerListCreateView(ListCreateAPIView):
    queryset = Banner.objects.all().order_by('-priority', 'created_at')
    serializer_class = BannerSerializer
    pagination_class = BannerPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        banner_type = self.request.query_params.get('banner_type')
        if banner_type:
            queryset = queryset.filter(banner_type=banner_type)
        position = self.request.query_params.get('position')
        if position:
            queryset = queryset.filter(position=position)
        return queryset

class BannerDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from .models import Banner
from .serializers import BannerSerializer

class BannerPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

class CustomerBannerListView(ListAPIView):
    queryset = Banner.objects.filter(is_active=True).order_by('-priority', 'created_at')
    serializer_class = BannerSerializer
    pagination_class = BannerPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        banner_type = self.request.query_params.get('banner_type')
        if banner_type:
            queryset = queryset.filter(banner_type=banner_type)
        position = self.request.query_params.get('position')
        if position:
            queryset = queryset.filter(position=position)
        return queryset