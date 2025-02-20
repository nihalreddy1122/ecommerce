from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .models import PriceRangeCommission
from .serializers import PriceRangeCommissionSerializer

# ------------------------------------------
# List and Create View for PriceRangeCommission
# Allows authenticated users to list all price ranges or create a new price range
# ------------------------------------------
class PriceRangeCommissionListCreateView(ListCreateAPIView):
    queryset = PriceRangeCommission.objects.all()
    serializer_class = PriceRangeCommissionSerializer
    permission_classes = [IsAuthenticated]

# ------------------------------------------
# Retrieve, Update, and Delete View for PriceRangeCommission
# Allows authenticated users to manage a specific price range
# ------------------------------------------
class PriceRangeCommissionDetailView(RetrieveUpdateDestroyAPIView):
    queryset = PriceRangeCommission.objects.all()
    serializer_class = PriceRangeCommissionSerializer
    permission_classes = [IsAuthenticated]
