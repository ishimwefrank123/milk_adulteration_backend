from django.db import models

class MilkData(models.Model):
    ph = models.FloatField()
    temperature = models.FloatField() # Corresponds to 'Temprature' in your CSV
    taste = models.FloatField(default=0.0)
    odor = models.FloatField(default=0.0)
    fat = models.FloatField(default=0.0)
    turbidity = models.FloatField(default=0.0)
    colour = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MilkData (pH: {self.ph}, Temp: {self.temperature}) at {self.timestamp}"