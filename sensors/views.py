from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import MilkData
from .serializers import MilkDataSerializer

class MilkDataCreateView(generics.ListCreateAPIView):
    """
    GET  /api/sensors/data/
    POST /api/sensors/data/
    """
    queryset = MilkData.objects.all().order_by('-timestamp')
    serializer_class = MilkDataSerializer
    permission_classes = [IsAuthenticated]