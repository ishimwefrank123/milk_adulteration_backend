from rest_framework import serializers
from .models import AnalysisResult

class AnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisResult
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get('status') == 'PURE':
            data.pop('adulteration_type', None)
            data.pop('percentage', None)
        return data