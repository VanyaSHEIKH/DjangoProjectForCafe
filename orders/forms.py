from django import forms
from .models import Order
import json


# Создание нового заказа
class OrderForm(forms.ModelForm):
    items_json = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': '[{"name":"Блюдо","price":100,"quantity":1}]'}),
        help_text='[{"name":"Капучино","price":150,"quantity":1}]'
    )

    class Meta:
        model = Order
        fields = ['table_number']
        widgets = {
            'table_number': forms.NumberInput(attrs={'min': 1})
        }

    # валидация JSON строки с блюдами
    def clean_items_json(self):
        data = self.cleaned_data['items_json']
        try:
            data = data.replace("'", '"')
            items = json.loads(data)

            if not isinstance(items, list):
                raise forms.ValidationError("Должен быть массив блюд")

            for item in items:
                if not isinstance(item, dict):
                    raise forms.ValidationError("Каждый элемент должен быть объектом")

                # Проверка обязательных полей
                if 'name' not in item or not item['name']:
                    raise forms.ValidationError("Укажите название блюда")

                if 'price' not in item or not isinstance(item['price'], (int, float)) or item['price'] <= 0:
                    raise forms.ValidationError("Укажите корректную цену (положительное число)")

                if 'quantity' in item and (not isinstance(item['quantity'], int) or item['quantity'] <= 0):
                    raise forms.ValidationError("Количество должно быть положительным целым числом")

            return items
        except json.JSONDecodeError as e:
            raise forms.ValidationError(
                f"Неверный JSON формат. Ошибка: {str(e)}. Пример: [{"name\":\"Кофе\",\"price":150}]")

    # Сохранение заказа
    def save(self, commit=True):
        order = super().save(commit=False)
        order.items = self.cleaned_data['items_json']
        if commit:
            order.save()
        return order

    # Проверка занятости стола
    def clean_table_number(self):
        table_number = self.cleaned_data['table_number']
        status = self.cleaned_data.get('status', 'pending')

        if status in ['pending', 'ready']:
            existing_orders = Order.objects.filter(
                table_number=table_number,
                status__in=['pending', 'ready']
            )

            if self.instance and self.instance.pk:
                existing_orders = existing_orders.exclude(pk=self.instance.pk)

            if existing_orders.exists():
                raise forms.ValidationError(
                    f'Стол {table_number} уже занят. Выберите другой столик. '

                )

        return table_number


# Изменение статуса заказа, только поле статус доступно для изменения
class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        labels = {
            'status': 'Новый статус'
        }
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'})
        }


# Изменение заказа
class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['table_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("Доступные поля формы:", self.fields.keys())  # Отладочная печать

        # Динамическое создание полей для каждого блюда
        if self.instance and hasattr(self.instance, 'items'):
            for i, item in enumerate(self.instance.items):
                self.fields[f'dish_{i}_name'] = forms.CharField(
                    initial=item.get('name', ''),
                    label=f'Блюдо {i + 1} - Название')
                self.fields[f'dish_{i}_quantity'] = forms.IntegerField(
                    initial=item.get('quantity', 1),
                    label='Количество')
                self.fields[f'dish_{i}_delete'] = forms.BooleanField(
                    label='Удалить',
                    required=False)

        # Поля для добавления нового блюда
        self.fields['new_dish_name'] = forms.CharField(label='Новое блюдо', required=False)
        self.fields['new_dish_quantity'] = forms.IntegerField(
            label='Количество',
            required=False,
            initial=1)
