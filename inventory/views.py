from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Inventory, StorageTank
from .serializers import InventorySerializer, StorageTankSerializer
from notifications.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class InventoryListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/inventory/
    POST /api/inventory/
    """
    queryset = Inventory.objects.all().order_by('-updated_at')
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

class StorageTankListCreateView(generics.ListCreateAPIView):
    queryset = StorageTank.objects.all().order_by('-updated_at')
    serializer_class = StorageTankSerializer
    permission_classes = [IsAuthenticated]

class TankLevelUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            tank = StorageTank.objects.get(pk=pk)
        except StorageTank.DoesNotExist:
            return Response({"error": "Tank not found"}, status=404)
        
        level = request.data.get('level')
        if level is not None:
            tank.current_level = float(level)
            tank.save()
            
            if tank.fill_percentage < 20:
                sellers = User.objects.filter(role='SELLER')
                for seller in sellers:
                    Notification.objects.create(
                        user=seller,
                        message=f"Alert: Tank '{tank.name}' is running low ({tank.fill_percentage:.1f}%)."
                    )
            return Response({"status": "success", "current_level": tank.current_level})
        return Response({"error": "No level provided"}, status=400)

class SellMilkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            tank = StorageTank.objects.get(pk=pk)
        except StorageTank.DoesNotExist:
            return Response({"error": "Tank not found"}, status=404)
        
        quantity = request.data.get('quantity')
        if quantity:
            quantity = float(quantity)
            if tank.current_level >= quantity:
                tank.current_level -= quantity
                tank.save()
                
                if tank.fill_percentage < 20:
                    sellers = User.objects.filter(role='SELLER')
                    for seller in sellers:
                        Notification.objects.create(
                            user=seller,
                            message=f"Alert: Tank '{tank.name}' is running low ({tank.fill_percentage:.1f}%)."
                        )
                return Response({"status": "success", "current_level": tank.current_level, "sold": quantity})
            else:
                return Response({"error": "Not enough milk in tank"}, status=400)
        return Response({"error": "No quantity provided"}, status=400)

class AddMilkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            tank = StorageTank.objects.get(pk=pk)
        except StorageTank.DoesNotExist:
            return Response({"error": "Tank not found"}, status=404)
        
        quantity = request.data.get('quantity')
        if quantity:
            quantity = float(quantity)
            if tank.current_level + quantity <= tank.capacity:
                tank.current_level += quantity
                tank.save()
                return Response({"status": "success", "current_level": tank.current_level, "added": quantity})
            else:
                return Response({"error": "Tank capacity exceeded! Cannot fit that much milk."}, status=400)
        return Response({"error": "No quantity provided"}, status=400)

class SupplierListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        suppliers = User.objects.filter(role='SUPPLIER')
        data = [{"id": s.id, "email": s.email, "name": s.username} for s in suppliers]
        return Response(data)

class RestockRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        supplier_id = request.data.get('supplier_id')
        message = request.data.get('message', "Restock requested.")
        
        try:
            supplier = User.objects.get(id=supplier_id, role='SUPPLIER')
        except User.DoesNotExist:
            return Response({"error": "Supplier not found"}, status=404)
            
        Notification.objects.create(
            user=supplier,
            message=f"Restock Request from {request.user.email}: {message}"
        )
        return Response({"status": "success"})

class RestockReplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        notification_id = request.data.get('notification_id')
        quantity = request.data.get('quantity')
        message = request.data.get('message', '')

        if not quantity:
            return Response({"error": "Quantity is required"}, status=400)

        if notification_id:
            try:
                notif = Notification.objects.get(id=notification_id, user=request.user)
                notif.read = True
                notif.save()
            except Notification.DoesNotExist:
                pass

        sellers = User.objects.filter(role='SELLER')
        msg = f"Supplier {request.user.username} acknowledged the restock request and can deliver {quantity}L."
        if message:
            msg += f" Note: {message}"

        for seller in sellers:
            Notification.objects.create(user=seller, message=msg)

        return Response({"status": "success"})