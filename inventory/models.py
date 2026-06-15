from django.db import models

class Inventory(models.Model):
    milk_quantity = models.FloatField()
    status = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Inventory - {self.milk_quantity}L ({self.status})"

class StorageTank(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.FloatField(help_text="Capacity in liters")
    current_level = models.FloatField(help_text="Current level in liters", default=0.0)
    location = models.CharField(max_length=100, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def fill_percentage(self):
        if self.capacity > 0:
            return (self.current_level / self.capacity) * 100
        return 0

    def __str__(self):
        return f"{self.name} ({self.current_level}/{self.capacity} L)"