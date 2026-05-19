from django.urls import path
from .views import InventoryListCreateView

urlpatterns = [
    path('', InventoryListCreateView.as_view(), name='inventory-list-create'),
]