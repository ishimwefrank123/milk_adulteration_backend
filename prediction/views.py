from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from analysis.models import AnalysisResult
from analysis.serializers import AnalysisResultSerializer

class PredictionListView(generics.ListAPIView):
    """
    GET /api/predictions/
    """
    queryset = AnalysisResult.objects.all().order_by('-created_at')
    serializer_class = AnalysisResultSerializer
    permission_classes = [IsAuthenticated]

class PredictionDetailView(generics.RetrieveAPIView):
    """
    GET /api/predictions/<id>/
    """
    queryset = AnalysisResult.objects.all()
    serializer_class = AnalysisResultSerializer
    permission_classes = [IsAuthenticated]