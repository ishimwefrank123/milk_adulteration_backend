from django.db import models

class Alert(models.Model):
    SEVERITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    )
    message = models.TextField()
    severity = models.CharField(max_length=15, choices=SEVERITY_CHOICES, default='HIGH')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Alert: {self.severity} - {self.created_at}"