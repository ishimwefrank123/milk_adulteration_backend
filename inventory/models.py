from django.db import models

class Inventory(models.Model):
    milk_quantity = models.FloatField()
    status = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Inventory - {self.milk_quantity}L ({self.status})"