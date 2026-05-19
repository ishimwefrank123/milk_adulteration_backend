from django.urls import path
from .views import MilkDataCreateView

urlpatterns = [
    path('data/', MilkDataCreateView.as_view(), name='sensor-data'),
]