from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import AnalysisResult
from .serializers import AnalysisResultSerializer
from sensors.serializers import MilkDataSerializer
from alerts.models import Alert

class AnalyzeMilkView(APIView):
    """
    POST /api/analyze/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1. Save incoming sensor data
        milk_data_serializer = MilkDataSerializer(data=request.data)
        if not milk_data_serializer.is_valid():
            return Response(milk_data_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        milk_data = milk_data_serializer.save()
        
        # 2. PLACEHOLDER ML INFERENCE
        # Replace this block later with your actual ML model logic 
        if milk_data.ph < 6.4 or milk_data.ph > 6.8 or milk_data.turbidity > 50:
            result_status = 'BAD'
            adulteration_type = 'Water' if milk_data.turbidity > 60 else 'Urea'
            percentage = 18.0
            reasons = 'Abnormal pH or High Turbidity detected.'
        else:
            result_status = 'GOOD'
            adulteration_type = None
            percentage = 0.0
            reasons = 'All parameters are within normal range.'
        # END OF PLACEHOLDER
        
        # 3. Save the findings
        analysis = AnalysisResult.objects.create(
            milk_data=milk_data,
            status=result_status,
            adulteration_type=adulteration_type,
            percentage=percentage,
            reasons=reasons
        )
        
        # 4. Trigger alert automatically if BAD
        if result_status == 'BAD':
            msg = f"Adulterated milk detected! Type: {adulteration_type}, Percentage: {percentage}%"
            Alert.objects.create(message=msg, severity='HIGH')
            
        return Response(AnalysisResultSerializer(analysis).data, status=status.HTTP_201_CREATED)