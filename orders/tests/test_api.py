import pytest
from rest_framework.test import APIClient


# Проверка создания заказа через API
@pytest.mark.django_db
def test_api_create_order():
    client = APIClient()
    response = client.post('/api/SubmitData/', {
        'table_number': 1,
        'items': [{'name': 'Кофе', 'price': 100, 'quantity': 1}]
    }, format='json')
    assert response.status_code == 201


# Тест получения списка заказов через API
@pytest.mark.django_db
def test_api_get_orders(api_client, order_factory):
    order_factory(table_number=1)  # Создает тестовый заказ через фабрику
    response = api_client.get('/api/SubmitData/')
    assert response.status_code == 200
    assert len(response.data) > 0


# Проверяет обновления статуса заказа через API
@pytest.mark.django_db
def test_api_update_order(api_client, order_factory):
    order = order_factory(status='pending')
    response = api_client.patch(
        f'/api/SubmitData/{order.id}/status/',
        {'status': 'ready'},
        format='json'
    )
    # Обновляет объект заказа из БД и проверяет изменение статуса
    assert response.status_code == 200
    order.refresh_from_db()
    assert order.status == 'ready'
