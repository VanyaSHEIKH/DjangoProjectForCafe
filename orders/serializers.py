from rest_framework import serializers
from .models import Order
from decimal import Decimal


# Для элементов заказа
class OrderItemSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    quantity = serializers.IntegerField(min_value=1, default=1)


# Для заказа
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'table_number',
            'items',
            'total_price',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'total_price',
            'created_at',
            'updated_at'
        ]

    # Валидация номера стола
    def validate_table_number(self, value):
        if value < 1:
            raise serializers.ValidationError("Номер стола должен быть положительным числом")
        return value

    def validate_items(self, value):
        if not value:  # проверка на то ,что заказ не пустой
            raise serializers.ValidationError("Заказ должен содержать хотя бы одно блюдо")
        return value

    # метод создания нового закака
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        order.update_items(items_data)
        return order

    # Метод обновления существующего заказа
    def update(self, instance, validated_data):
        if 'items' in validated_data:  # Если в обновляемых данных есть элементы заказа
            instance.update_items(validated_data['items'])
        instance.table_number = validated_data.get('table_number', instance.table_number)
        instance.save()
        return instance


# Для обновления статуса заказа
class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        if value not in dict(Order.STATUS_CHOICES).keys():  # Проверка,что статус допустим
            raise serializers.ValidationError("Недопустимый статус заказа")
        return value
