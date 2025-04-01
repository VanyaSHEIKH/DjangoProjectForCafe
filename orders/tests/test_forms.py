import pytest
from orders.forms import OrderForm, OrderStatusForm, OrderEditForm
from orders.models import Order


# Фабрика для создания тестовых заказов
@pytest.fixture
def order_factory(db):
    def factory(**kwargs):
        # Значения для нового заказа
        defaults = {
            'table_number': 1,
            'items': [{'name': 'Кофе', 'price': 100, 'quantity': 1}],
            'status': 'pending',
            'total_price': 100
        }
        defaults.update(kwargs)
        return Order.objects.create(**defaults)

    return factory


# Проверка валидной формы заказа
@pytest.mark.django_db
def test_valid_order_form():
    # валидные данные для формы
    form_data = {
        'table_number': 1,
        'items_json': '[{"name":"Капучино","price":150,"quantity":1}]'
    }
    form = OrderForm(data=form_data)
    assert form.is_valid()
    assert form.cleaned_data['table_number'] == 1
    assert len(form.cleaned_data['items_json']) == 1


# Проверка невалидного JSON
@pytest.mark.django_db
def test_invalid_json_format():
    # Данные с невалидным JSON
    form = OrderForm(data={
        'table_number': 1,
        'items_json': 'invalid json'
    })
    assert not form.is_valid()
    assert 'items_json' in form.errors


# Проверка отсутствия обязательных полей
@pytest.mark.django_db
def test_missing_required_fields():
    # Данные без обязательного поля 'name'
    form = OrderForm(data={
        'table_number': 1,
        'items_json': '[{"price":150}]'
    })
    assert not form.is_valid()
    assert 'Укажите название блюда' in str(form.errors)


# Проверка валидации номера стола
@pytest.mark.django_db
def test_table_validation(order_factory):
    # Создает заказ занимающий стол 1
    order = order_factory(table_number=1, status='pending')
    # Создает новый заказ на тот же стол 1
    form = OrderForm(data={
        'table_number': 1,
        'items_json': '[{"name":"Кофе","price":100}]'
    })
    assert not form.is_valid()
    assert 'Стол 1 уже занят' in str(form.errors)


# Проверка формы изменения статуса
@pytest.mark.django_db
def test_order_status_form():
    # Создает форму с валидным статусом
    form = OrderStatusForm(data={'status': 'ready'})
    assert form.is_valid()
    assert form.cleaned_data['status'] == 'ready'
