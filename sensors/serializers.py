from rest_framework import serializers
from .models import MilkData

class MilkDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilkData
        fields = '__all__'