from django.urls import path
from .views import OrderList, OrderCreate, OrderStatusUpdate, OrderDelete, OrderRevenue, OrderUpdate

urlpatterns = [
    path('', OrderList.as_view(), name='order_list'),
    path('create/', OrderCreate.as_view(), name='order_create'),
    path('<int:pk>/status/', OrderStatusUpdate.as_view(), name='order_status_update'),
    path('<int:pk>/delete/', OrderDelete.as_view(), name='order_delete'),
    path('revenue/', OrderRevenue.as_view(), name='revenue'),
    path('<int:pk>/edit/', OrderUpdate.as_view(), name='order_edit'),
]