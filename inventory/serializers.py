from rest_framework import serializers
from .models import Inventory, StorageTank

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ['id', 'milk_quantity', 'status', 'updated_at']

class StorageTankSerializer(serializers.ModelSerializer):
    fill_percentage = serializers.ReadOnlyField()

    class Meta:
        model = StorageTank
        fields = ['id', 'name', 'capacity', 'current_level', 'location', 'updated_at', 'fill_percentage']