from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


# Модель заказа
class Order(models.Model):
    # Варианты статусов заказа
    STATUS_PENDING = 'pending'
    STATUS_READY = 'ready'
    STATUS_PAID = 'paid'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'В ожидании'),
        (STATUS_READY, 'Готово'),
        (STATUS_PAID, 'Оплачено'),
    ]

    # Номер стола (только положительные числа)
    table_number = models.PositiveIntegerField(verbose_name="Номер стола", validators=[MinValueValidator(1)],
                                               help_text="Введите номер стола (1, 2, 3...)")

    # Список блюд в формате JSON
    items = models.JSONField(verbose_name="Список блюд", default=list)

    # Общая сумма заказа (автоматически рассчитывается)
    total_price = models.DecimalField(verbose_name="Общая сумма", max_digits=10, decimal_places=2, default=0)

    # Текущий статус заказа
    status = models.CharField(verbose_name="Статус", max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, )

    # Дата создания
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)

    # Дата обновления
    updated_at = models.DateTimeField(verbose_name="Дата обновления", auto_now=True)

    def clean(self):
        # Проверка, не занят ли стол
        if self.status in ['pending', 'ready']:
            existing_orders = Order.objects.filter(table_number=self.table_number, status__in=['pending', 'ready']
                                                   ).exclude(pk=self.pk)

            if existing_orders.exists():
                raise ValidationError(
                    f'Стол {self.table_number} уже имеет активный заказ. '
                    'Завершите текущий заказ перед созданием нового.'
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # Рассчитывает общую сумму заказа на основе списка блюд
    def calculate_total(self):
        total = 0
        for item in self.items:
            price = item['price']
            quantity = item.get('quantity', 1)
            total += price * quantity

        self.total_price = total
        return total

    def save(self, *args, **kwargs):
        self.calculate_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Заказ #{self.id} (Стол {self.table_number})"

    # Обновляет список блюд в заказе с валидацией
    def update_items(self, new_items):
        validated_items = []
        for item in new_items:
            if item.get('name') and item.get('price'):
                validated_items.append({
                    'name': item['name'],
                    'price': float(item['price']),
                    'quantity': int(item.get('quantity', 1))
                })
        self.items = validated_items
        self.save()

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']
