from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from analysis.models import AnalysisResult

class DashboardSummaryView(APIView):
    """
    GET /api/dashboard/summary/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_samples = AnalysisResult.objects.count()
        bad_milk = AnalysisResult.objects.filter(status='BAD').count()
        good_milk = AnalysisResult.objects.filter(status='GOOD').count()
        
        return Response({
            "total_samples": total_samples,
            "number_of_bad_milk": bad_milk,
            "number_of_good_milk": good_milk
        })