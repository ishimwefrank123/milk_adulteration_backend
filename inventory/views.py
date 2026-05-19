from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Inventory
from .serializers import InventorySerializer

class InventoryListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/inventory/
    POST /api/inventory/
    """
    queryset = Inventory.objects.all().order_by('-updated_at')
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]