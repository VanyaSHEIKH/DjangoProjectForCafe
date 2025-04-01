import pytest
import os
import django
from django.conf import settings


# Функция настройки pytest
def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'cafe.settings')  # Устанавливает переменную окружения DJANGO_SETTINGS_MODULE,указывающую на файл настроек проекта (cafe.settings)
    django.setup()


# фабрика для создания тестов
@pytest.fixture
def order_factory(db):
    from orders.models import Order
    def create_order(**kwargs):
        # Значения для нового заказа
        defaults = {
            'table_number': 1,
            'items': [{'name': 'Кофе', 'price': 100, 'quantity': 1}],
            'status': 'pending'
        }
        defaults.update(kwargs)
        return Order.objects.create(**defaults)

    return create_order


# Фикстура для создания API клиента
@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()
