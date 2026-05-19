from django.db import models

class MilkData(models.Model):
    ph = models.FloatField()
    temperature = models.FloatField()
    gas = models.FloatField()
    turbidity = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MilkData (pH: {self.ph}, Temp: {self.temperature}) at {self.timestamp}"