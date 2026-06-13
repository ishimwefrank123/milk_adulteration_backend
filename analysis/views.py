from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import AnalysisResult
from .serializers import AnalysisResultSerializer
from sensors.serializers import MilkDataSerializer
from sensors.ml_service import predict_milk_quality
from alerts.models import Alert


class AnalysisResultListView(generics.ListAPIView):
    """
    GET /api/analyze/results/
    """
    queryset = AnalysisResult.objects.all().order_by('-created_at')
    serializer_class = AnalysisResultSerializer
    permission_classes = [IsAuthenticated]


class LatestAnalysisView(APIView):
    """
    GET /api/analyze/latest/  — returns the most recent analysis result
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        latest = AnalysisResult.objects.select_related('milk_data').order_by('-created_at').first()
        if not latest:
            return Response({
                'status': 'GOOD',
                'ph': None, 'temperature': None,
                'taste': None, 'odor': None,
                'fat': None, 'turbidity': None, 'colour': None,
                'adulteration_type': None,
                'percentage': 0,
                'reasons': [],
            })

        md = latest.milk_data
        reasons_raw = latest.reasons or ''
        reasons = [r.strip() for r in reasons_raw.split('.') if r.strip()]

        return Response({
            'id':                latest.id,
            'status':            latest.status,
            'adulteration_type': latest.adulteration_type,
            'percentage':        latest.percentage,
            'reasons':           reasons,
            'created_at':        latest.created_at,
            'ph':          md.ph          if md else None,
            'temperature': md.temperature if md else None,
            'taste':       md.taste       if md else None,
            'odor':        md.odor        if md else None,
            'fat':         md.fat         if md else None,
            'turbidity':   md.turbidity   if md else None,
            'colour':      md.colour      if md else None,
        })


class AnalyzeMilkView(APIView):
    """
    POST /api/analyze/
    Accepts: ph, temperature, taste, odor, fat, turbidity, colour
    Runs XGBoost ML model and returns: status, adulteration_type, percentage, reasons
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1. Validate and save sensor data
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
        
        # 4. Trigger alert automatically
        if ml_results['status'] == 'BAD':
            msg = f"Adulterated milk detected! Type: {ml_results['adulteration_type'] or 'Unknown'}, Percentage: {ml_results['percentage']}%. Reasons: {ml_results['reasons']}"
            Alert.objects.create(message=msg, severity='HIGH')
        else:
            msg = f"Pure milk recorded! Quality is good. Reasons: {ml_results['reasons']}"
            Alert.objects.create(message=msg, severity='LOW')
            
        from notifications.models import Notification
        Notification.objects.create(user=request.user, message=msg)
            
        return Response(AnalysisResultSerializer(analysis).data, status=status.HTTP_201_CREATED)
