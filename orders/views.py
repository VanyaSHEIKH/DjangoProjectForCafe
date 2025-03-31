from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from django.db.models import Sum
from .models import Order
from .forms import OrderForm, OrderStatusForm, OrderEditForm
from django.contrib import messages

#Список заказов с поиском по номеру заказа и стола
class OrderList(ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    #Добавляет поиск по номеру заказа иои стола
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '').strip()

        if search_query and search_query.isdigit():
            search_number = int(search_query)
            queryset = queryset.filter(
                id=search_number
            ) | queryset.filter(
                table_number=search_number
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

#Создает новый заказ
class OrderCreate(CreateView):
    """
    Создание нового заказа
    """
    model = Order  # Работаем с моделью Order
    form_class = OrderForm  # Используем нашу форму
    template_name = 'order_create.html'  # Шаблон формы
    success_url = reverse_lazy('order_list')  # Куда перейти после успеха

    #Устанавливает статус pending по умолчанию
    def form_valid(self, form):
        form.instance.status = 'pending'
        return super().form_valid(form)
    #Обработка невалидной формы
    def form_invalid(self, form):
        messages.error(self.request, 'Не удалось создать заказ. Исправьте ошибки.')
        return super().form_invalid(form)

#Изменение статуса заказа
class OrderStatusUpdate(UpdateView):
    model = Order
    form_class = OrderStatusForm
    template_name = 'order_status_update.html'
    success_url = reverse_lazy('order_list')

#Удаление заказа
class OrderDelete(DeleteView):
    model = Order
    template_name = 'order_delete.html'
    success_url = reverse_lazy('order_list')

#Отчет по выручке с оплаченных заказов
class OrderRevenue(TemplateView):
    template_name = 'revenue.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Считает общую выручку по оплаченным заказам
        context['total_revenue'] = Order.objects.filter(
            status=Order.STATUS_PAID
        ).aggregate(Sum('total_price'))['total_price__sum'] or 0

        # Получает все оплаченные заказы
        context['paid_orders'] = Order.objects.filter(
            status=Order.STATUS_PAID
        ).order_by('-created_at')

        return context

#Редактирование заказа
class OrderUpdate(UpdateView):
    model = Order
    template_name = 'order_edit.html'
    success_url = reverse_lazy('order_list')
    fields = []

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        updated_items = []

        #Получает данные из формы
        names = request.POST.getlist('dish_name')
        prices = request.POST.getlist('dish_price')
        quantities = request.POST.getlist('dish_quantity')
        deletes = request.POST.getlist('dish_delete')

        #Обрабатывает существующие блюда
        for i in range(len(names)):
            if str(i) not in deletes:
                try:
                    updated_items.append({
                        'name': names[i],
                        'price': float(prices[i]),
                        'quantity': int(quantities[i])
                    })
                except (ValueError, IndexError):
                    continue

        #Добавляет новое блюдо
        new_name = request.POST.get('new_dish_name', '').strip()
        new_price = request.POST.get('new_dish_price')
        if new_name and new_price:
            try:
                updated_items.append({
                    'name': new_name,
                    'price': float(new_price),
                    'quantity': int(request.POST.get('new_dish_quantity', 1))
                })
            except ValueError:
                pass

        order.items = updated_items
        order.save()

        messages.success(request, 'Заказ успешно обновлен!')
        return super().post(request, *args, **kwargs)