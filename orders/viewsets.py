from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Order
from .serializers import OrderSerializer, OrderStatusSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')  # Получает все заказы, сортируя их по дате создания
    serializer_class = OrderSerializer

    @action(detail=True, methods=['patch'])  # Определяет действие для обновления статуса заказа
    def status(self, request, pk=None):
        # Метод для изменения статуса заказа по его идентификатору
        order = self.get_object()
        serializer = OrderStatusSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])  # Определяет действие для получения общей выручки
    def revenue(self, request):
        from django.db.models import Sum  # Импортируем функцию Sum для агрегирования данных
        total = Order.objects.filter(status=Order.STATUS_PAID).aggregate(
            Sum('total_price'))
        return Response({
            'total_revenue': total['total_price__sum'] or 0  # Возвращает общую выручку или 0, если выручки нет
        })
