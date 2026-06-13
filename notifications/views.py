from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification

class NotificationListView(APIView):
    """
    GET /api/notifications/  — returns recent notifications for user
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
        data = [
            {
                'id': n.id,
                'message': n.message,
                'read': n.read,
                'created_at': n.created_at,
            }
            for n in notifs
        ]
        return Response(data)

class NotificationDetailView(APIView):
    """
    PATCH /api/notifications/<id>/ — mark as read
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, pk):
        try:
            n = Notification.objects.get(pk=pk, user=request.user)
            if 'read' in request.data:
                n.read = request.data['read']
                n.save()
            return Response({'id': n.id, 'read': n.read, 'message': n.message})
        except Notification.DoesNotExist:
            return Response(status=404)
