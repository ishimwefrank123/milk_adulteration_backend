from rest_framework import serializers
from .models import Inventory

class InventorySerializer(serializers.ModelSerializer):
    quantity = serializers.FloatField(source='milk_quantity')

    class Meta:
        model = Inventory
        fields = ['id', 'quantity', 'status', 'updated_at']