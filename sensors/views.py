from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import MilkData
from .serializers import MilkDataSerializer

class MilkDataCreateView(generics.CreateAPIView):
    """
    POST /api/sensors/data/
    """
    queryset = MilkData.objects.all()
    serializer_class = MilkDataSerializer
    permission_classes = [IsAuthenticated]