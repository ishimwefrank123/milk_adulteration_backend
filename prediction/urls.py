from django.urls import path
from .views import PredictionListView, PredictionDetailView

urlpatterns = [
    path('', PredictionListView.as_view(), name='prediction-list'),
    path('<int:pk>/', PredictionDetailView.as_view(), name='prediction-detail'),
]