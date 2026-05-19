from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Alert
from .serializers import AlertSerializer

class AlertListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/alerts/
    POST /api/alerts/
    """
    queryset = Alert.objects.all().order_by('-created_at')
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]