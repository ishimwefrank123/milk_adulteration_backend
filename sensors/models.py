from django.db import models


class MilkData(models.Model):
    ph = models.FloatField(default=0.0)           # analog pH sensor
    temperature = models.FloatField(default=0.0)  # DS18B20/DHT22, Celsius
    taste = models.FloatField(default=0.0)        # quality proxy: 0=abnormal, 1=normal
    odor = models.FloatField(default=0.0)         # MQ gas sensor proxy: 0=abnormal, 1=normal
    fat = models.FloatField(default=0.0)          # fat content %
    turbidity = models.FloatField(default=0.0)    # turbidity sensor, NTU
    colour = models.FloatField(default=0.0)       # colour sensor value, usually 240-255
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MilkData (pH: {self.ph}, Temp: {self.temperature}) at {self.timestamp}"
