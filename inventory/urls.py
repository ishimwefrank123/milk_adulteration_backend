from django.urls import path
from .views import (
    InventoryListCreateView,
    StorageTankListCreateView,
    TankLevelUpdateView,
    SellMilkView,
    SupplierListView,
    RestockRequestView,
    RestockReplyView,
    AddMilkView
)

urlpatterns = [
    path('', InventoryListCreateView.as_view(), name='inventory-list-create'),
    path('tanks/', StorageTankListCreateView.as_view(), name='tanks-list'),
    path('tanks/<int:pk>/level/', TankLevelUpdateView.as_view(), name='tank-level-update'),
    path('tanks/<int:pk>/sell/', SellMilkView.as_view(), name='tank-sell-milk'),
    path('tanks/<int:pk>/add/', AddMilkView.as_view(), name='tank-add-milk'),
    path('suppliers/', SupplierListView.as_view(), name='supplier-list'),
    path('restock/', RestockRequestView.as_view(), name='restock-request'),
    path('restock/reply/', RestockReplyView.as_view(), name='restock-reply'),
]