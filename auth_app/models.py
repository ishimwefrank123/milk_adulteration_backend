from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('SUPPLIER', 'Supplier'),
        ('SELLER', 'Seller'),
        ('ADMIN', 'Admin'),
    )
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='SUPPLIER')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Django still needs username internally

    def __str__(self):
        return f"{self.email} ({self.role})"