from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from alerts.models import Alert


class NotificationListView(APIView):
    """
    GET /api/notifications/  — returns recent alerts as notifications
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        alerts = Alert.objects.order_by('-created_at')[:10]
        data = [
            {
                'id': a.id,
                'message': a.message,
                'read': False,
            }
            for a in alerts
        ]
        return Response(data)
