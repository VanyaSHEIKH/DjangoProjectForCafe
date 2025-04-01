import pytest
from django.urls import reverse


# Проверка отображения списка заказов
@pytest.mark.django_db
def test_order_list_view(client, order_factory):
    # Тестовый заказ
    order_factory()
    response = client.get(reverse('order_list'))
    assert response.status_code == 200
    assert 'orders' in response.context


# Проверка создания заказа
@pytest.mark.django_db
def test_create_order(client):
    response = client.post(reverse('order_create'), {
        'table_number': 1,
        'items_json': '[{"name":"Чай","price":50,"quantity":1}]'
    })
    assert response.status_code == 302  # Редирект после успеха


# Тест изменения статуса заказа
@pytest.mark.django_db
def test_update_status(api_client, order_factory):
    order = order_factory(status='pending')
    response = api_client.patch(
        f'/api/SubmitData/{order.id}/status/',
        {'status': 'ready'},
        format='json'
    )
    assert response.status_code == 200
    order.refresh_from_db()
    assert order.status == 'ready'
