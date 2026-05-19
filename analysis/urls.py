from django.urls import path
from .views import AnalyzeMilkView

urlpatterns = [
    path('', AnalyzeMilkView.as_view(), name='analyze-milk'),
]