from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import MilkData
from .serializers import MilkDataSerializer
from prediction.ml_service import predict_milk_quality


class MilkDataCreateView(generics.CreateAPIView):
    """
    POST /api/sensors/data/
    """

    queryset = MilkData.objects.all()
    serializer_class = MilkDataSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        data = serializer.validated_data

        try:
            prediction = predict_milk_quality(
                ph=data["ph"],
                temperature=data["temperature"],
                taste=data["taste"],
                odor=data["odor"],
                fat=data["fat"],
                turbidity=data["turbidity"],
                colour=data["colour"],
            )

        except Exception as e:
            prediction = {
                "status": "ERROR",
                "adulteration_type": None,
                "percentage": 0,
                "reasons": str(e),
            }

        response_data = serializer.data
        response_data["ml_analysis"] = prediction

        headers = self.get_success_headers(serializer.data)

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )