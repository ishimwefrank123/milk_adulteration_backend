from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from analysis.models import AnalysisResult
from alerts.models import Alert
from sensors.models import MilkData
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardSummaryView(APIView):
    """
    GET /api/dashboard/summary/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_samples = AnalysisResult.objects.count()
        bad_milk = AnalysisResult.objects.filter(status='BAD').count()
        good_milk = AnalysisResult.objects.filter(status='GOOD').count()
        total_alerts = Alert.objects.count()
        total_users = User.objects.count()
        total_sensors = MilkData.objects.count()

        recent_results = AnalysisResult.objects.select_related('milk_data').order_by('-created_at')[:10]
        recent_data = []
        for r in recent_results:
            recent_data.append({
                'id': r.id,
                'status': r.status,
                'adulteration_type': r.adulteration_type,
                'percentage': r.percentage,
                'reasons': r.reasons,
                'created_at': r.created_at,
                'ph': r.milk_data.ph if r.milk_data else None,
                'temperature': r.milk_data.temperature if r.milk_data else None,
                'odor': r.milk_data.odor if r.milk_data else None,
                'turbidity': r.milk_data.turbidity if r.milk_data else None,
            })

        recent_alerts = list(Alert.objects.order_by('-created_at')[:5].values(
            'id', 'message', 'severity', 'created_at'
        ))

        users_list = list(User.objects.values('id', 'email', 'username', 'role', 'is_active'))

        return Response({
            "total_samples": total_samples,
            "number_of_bad_milk": bad_milk,
            "number_of_good_milk": good_milk,
            "total_alerts": total_alerts,
            "total_users": total_users,
            "total_sensors": total_sensors,
            "recent_results": recent_data,
            "recent_alerts": recent_alerts,
            "users": users_list,
        })
