from rest_framework import serializers
from .models import AnalysisResult


class AnalysisResultSerializer(serializers.ModelSerializer):
    # Flatten sensor fields from the related MilkData object
    ph          = serializers.FloatField(source='milk_data.ph',          read_only=True)
    temperature = serializers.FloatField(source='milk_data.temperature', read_only=True)
    taste       = serializers.FloatField(source='milk_data.taste',       read_only=True)
    odor        = serializers.FloatField(source='milk_data.odor',        read_only=True)
    fat         = serializers.FloatField(source='milk_data.fat',         read_only=True)
    turbidity   = serializers.FloatField(source='milk_data.turbidity',   read_only=True)
    colour      = serializers.FloatField(source='milk_data.colour',      read_only=True)

    # Convert stored reasons string → list for the frontend
    reasons = serializers.SerializerMethodField()

    def get_reasons(self, obj):
        if not obj.reasons:
            return []
        if isinstance(obj.reasons, list):
            return obj.reasons
        return [r.strip() for r in obj.reasons.split('.') if r.strip()]

    class Meta:
        model = AnalysisResult
        fields = [
            'id', 'status', 'adulteration_type', 'percentage',
            'reasons', 'created_at',
            'ph', 'temperature', 'taste', 'odor', 'fat', 'turbidity', 'colour',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get('status') == 'PURE':
            data.pop('adulteration_type', None)
            data.pop('percentage', None)
        return data
