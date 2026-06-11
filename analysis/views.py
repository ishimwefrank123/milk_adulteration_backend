from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import AnalysisResult
from .serializers import AnalysisResultSerializer
from sensors.serializers import MilkDataSerializer
from alerts.models import Alert
from prediction.ml_service import predict_milk_quality
# Corrected import path to match your file structure


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
        
        # 2. ML INFERENCE
        try:
            # Pass all 7 features to the prediction function in the correct order
            ml_results = predict_milk_quality(
                ph=milk_data.ph,
                temperature=milk_data.temperature,
                taste=milk_data.taste,
                odor=milk_data.odor,
                fat=milk_data.fat,
                turbidity=milk_data.turbidity,
                colour=milk_data.colour
            )
        except Exception as e:
            return Response({"error": f"ML Prediction failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 3. Save the findings
        analysis = AnalysisResult.objects.create(
            milk_data=milk_data,
            status=ml_results['status'],
            adulteration_type=ml_results['adulteration_type'],
            percentage=ml_results['percentage'],
            reasons=ml_results['reasons']
        )
        
        # 4. Trigger alert automatically if ADULTERATED
        if ml_results['status'] == 'ADULTERATED':
            msg = f"Adulterated milk detected! Type: {ml_results['adulteration_type']}, Percentage: {ml_results['percentage']}%"
            Alert.objects.create(message=msg, severity='HIGH')
            
        return Response(AnalysisResultSerializer(analysis).data, status=status.HTTP_201_CREATED)