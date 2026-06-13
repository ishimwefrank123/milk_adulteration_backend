from django.urls import path
from .views import AnalyzeMilkView, AnalysisResultListView, LatestAnalysisView

urlpatterns = [
    path('', AnalyzeMilkView.as_view(), name='analyze-milk'),
    path('results/', AnalysisResultListView.as_view(), name='analyze-results'),
    path('latest/', LatestAnalysisView.as_view(), name='analyze-latest'),
]