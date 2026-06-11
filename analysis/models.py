from django.db import models
from sensors.models import MilkData

class AnalysisResult(models.Model):
    STATUS_CHOICES = (
        ('PURE', 'Pure'),
        ('ADULTERATED', 'Adulterated'),
    )
    
    milk_data = models.OneToOneField(MilkData, on_delete=models.CASCADE, related_name='analysis_result', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    adulteration_type = models.CharField(max_length=50, blank=True, null=True)
    percentage = models.FloatField(default=0.0)
    reasons = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Analysis - {self.status} ({self.created_at})"