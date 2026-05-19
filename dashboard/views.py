from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.contrib import messages
from .models import CrmOrder, Recall, FbForm
from datetime import date, timedelta
from decimal import Decimal
import time
import traceback


def dashboard(request):
    recent_orders = CrmOrder.objects.order_by('-date', '-id')[:5]

    orders_data = []
    for o in recent_orders:
        orders_data.append({
            'id': o.order_number or o.id,
            'customer': o.customer_name,
            'initials': o.initials,
            'product': ', '.join(o.product_list[:2]) if o.product_list else '—',
            'amount': f"{o.total_amount:,.0f}".replace(',', ' '),
            'status': o.status_label,
            'status_class': o.status_class,
        })

    chart_data = [
        {'label': 'Янв', 'total_height': 38.78, 'current_height': 23.27},
        {'label': 'Фев', 'total_height': 53.06, 'current_height': 31.84},
        {'label': 'Мар', 'total_height': 44.90, 'current_height': 26.94},
        {'label': 'Апр', 'total_height': 62.24, 'current_height': 37.35},
        {'label': 'Май', 'total_height': 48.98, 'current_height': 29.39},
        {'label': 'Июн', 'total_height': 73.47, 'current_height': 44.08},
        {'label': 'Июл', 'total_height': 66.33, 'current_height': 39.80},
        {'label': 'Авг', 'total_height': 82.65, 'current_height': 49.59},
        {'label': 'Сен', 'total_height': 77.55, 'current_height': 46.53},
        {'label': 'Окт', 'total_height': 93.88, 'current_height': 56.33},
        {'label': 'Ноя', 'total_height': 85.71, 'current_height': 51.43},
        {'label': 'Дек', 'total_height': 100, 'current_height': 60},
    ]

    tasks = [
        {'name': 'Продажи электроники', 'current': 42, 'target': 78, 'remaining': 46},
        {'name': 'Продажи одежды', 'current': 36, 'target': 65, 'remaining': 45},
        {'name': 'Новые клиенты', 'current': 28, 'target': 52, 'remaining': 46},
        {'name': 'Средний чек', 'current': 19, 'target': 34, 'remaining': 44},
    ]

    context = {
        'chart_data': chart_data,
        'tasks': tasks,
        'orders': orders_data,
    }
    return render(request, 'dashboard/index.html', context)


class OrderWrapper:
    STATUS_CHOICES = [
        (0, 'Новый'),
        (1, 'Отзыв'),
        (2, 'Подтверждён'),
        (3, 'В обработке'),
        (4, 'Отменён'),
        (5, 'Самовывоз'),
        (6, 'Отложен'),
        (7, 'Самовывоз собран'),
        (8, 'Приход'),
        (9, 'Расход'),
    ]

    CDEK_TARIFFS = [
        ('parcel_warehouse', 'Посылка склад-склад'),
        ('parcel_door', 'Посылка склад-дверь'),
        ('economy', 'Экономичная посылка'),
        ('express', 'Экспресс'),
        ('standard_door', 'Стандартная доставка до двери'),
    ]

    def __init__(self, crm_order):
        self._order = crm_order
        self._customer_name = None
        self._customer_last_name = None
        self._customer_phone = None
        self._customer_email = None
        self._customer_full_address = None
        self._customer_zip_code = None
        self._customer_region = None
        self._customer_street_address = None
        self.id = crm_order.id
        self.date = crm_order.date
        self.source = crm_order.source or 'Animal-hoods.ru'
        self.order_number = crm_order.order_number or ''
        self.courier_name = crm_order.curier_name or ''
        self.delivery_date = crm_order.delivery_date
        self.time_restrictions = crm_order.time_limit or ''
        self.status = crm_order.status
        self.total_amount = crm_order.total_amount
        self.delivery_cost_customer = float(crm_order.delivery_cost or 0)
        self.delivery_cost_actual = float(crm_order.delivery_expenses or 0)
        self.discount = float(crm_order.discount or 0)
        self.promo_discount = float(crm_order.discount_percent_promocode or 0)
        self.send_cdek = crm_order.sdek == 1
        self.cdek_tariff = crm_order.cdek_tariff_code or ''
        self.cdek_length = None
        self.cdek_width = None
        self.cdek_height = None
        self.cdek_weight = None
        self.cdek_city = crm_order.cdek_city_name or ''
        self.cdek_city_code = crm_order.cdek_city_code or ''
        self.cdek_pickup_address = crm_order.pvz_address or ''
        self.pvz_code = crm_order.pvz_code or ''
        self.cdek_address = crm_order.cdek_address or ''
        self.cdek_street = ''
        self.cdek_house = ''
        self.cdek_apartment = ''
        self.paid_status = crm_order.paid_status
        self.post_pay = crm_order.post_pay
        self.cashless = crm_order.cashless
        self.office_send = crm_order.office_send
        self.send_region = crm_order.send_region
        self.delivery_day = crm_order.delivery_day or ''
        self.note = crm_order.note or ''
        self.note_print = crm_order.note_print or ''
        self.way_of_pay_accept = crm_order.way_of_pay_accept or ''
        self.day_of_pay_accept = crm_order.day_of_pay_accept
        self.post_status = crm_order.post_status
        self.treck = crm_order.treck or ''
        self.delivery_summ = crm_order.delivery_summ or 0
        self.return_summ = crm_order.return_summ or 0
        self.sms = crm_order.sms
        self.sms_pay_info = crm_order.sms_pay_info
        self.sms_promocode = crm_order.sms_promocode
        self.call_back_email = crm_order.call_back_email
        self.recall_story = crm_order.recall_story or ''
        self.last_call_mark = crm_order.last_call_mark
        self.client_next_call = crm_order.client_next_call
        self.date_of_money_get = crm_order.date_of_money_get

        client_addr = crm_order.cdek_client_address or ''
        parts = client_addr.split('::') if client_addr else ['', '', '']
        if len(parts) >= 3:
            self.cdek_street = parts[0]
            self.cdek_house = parts[1]
            self.cdek_apartment = parts[2]

        pkg_sizes = crm_order.cdek_sizes_package or ''
        pkg_parts = pkg_sizes.split('::') if pkg_sizes else ['', '', '']
        if len(pkg_parts) >= 3:
            try:
                self.cdek_length = int(pkg_parts[0]) if pkg_parts[0] else None
                self.cdek_width = int(pkg_parts[1]) if pkg_parts[1] else None
                self.cdek_height = int(pkg_parts[2]) if pkg_parts[2] else None
            except ValueError:
                pass

    @property
    def customer(self):
        if not hasattr(self, '_customer_wrapper'):
            self._customer_wrapper = CustomerWrapper(self)
        return self._customer_wrapper

    @property
    def items(self):
        return OrderItemsWrapper(self._order)

    @property
    def status_class(self):
        classes = {
            0: 'bg-gradient-warm text-primary',
            1: 'bg-primary/10 text-primary',
            2: 'bg-accent/40 text-accent-foreground',
            3: 'bg-secondary text-secondary-foreground',
            4: 'bg-destructive/10 text-destructive',
            5: 'bg-secondary text-secondary-foreground',
            6: 'bg-secondary text-secondary-foreground',
            7: 'bg-secondary text-secondary-foreground',
            8: 'bg-accent/40 text-accent-foreground',
            9: 'bg-destructive/10 text-destructive',
        }
        return classes.get(self.status, 'bg-secondary text-secondary-foreground')

    @property
    def subtotal(self):
        return self.total_amount

    @property
    def total_with_delivery(self):
        return self.subtotal + self.delivery_cost_customer - self.discount - self.promo_discount

    def get_status_display(self):
        labels = {k: v for k, v in self.STATUS_CHOICES}
        return labels.get(self.status, 'Неизвестно')

    def save(self):
        o = self._order
        o.source = self.source
        o.order_number = self.order_number
        o.curier_name = self.courier_name
        o.delivery_date = self.delivery_date if self.delivery_date else None
        o.time_limit = self.time_restrictions
        o.status = self.status
        o.sdek = 1 if self.send_cdek else 0
        o.cdek_tariff_code = self.cdek_tariff
        o.delivery_cost = int(self.delivery_cost_customer)
        o.delivery_expenses = int(self.delivery_cost_actual)
        o.discount = int(self.discount)
        o.discount_percent_promocode = int(self.promo_discount)

        cdek_addr = '::'.join([self.cdek_street, self.cdek_house, self.cdek_apartment])
        o.cdek_client_address = cdek_addr

        pkg_parts = []
        for v in [self.cdek_length, self.cdek_width, self.cdek_height]:
            pkg_parts.append(str(v) if v is not None else '')
        o.cdek_sizes_package = '::'.join(pkg_parts)

        o.cdek_city_name = self.cdek_city
        o.cdek_city_code = self.cdek_city_code
        o.pvz_address = self.cdek_pickup_address
        o.pvz_code = self.pvz_code
        o.cdek_address = self.cdek_address

        o.paid_status = self.paid_status
        o.post_pay = self.post_pay
        o.cashless = self.cashless
        o.office_send = self.office_send
        o.send_region = self.send_region
        o.delivery_day = self.delivery_day
        o.note = self.note
        o.note_print = self.note_print
        o.way_of_pay_accept = self.way_of_pay_accept
        o.day_of_pay_accept = self.day_of_pay_accept if self.day_of_pay_accept else None
        o.post_status = self.post_status
        o.treck = self.treck
        o.delivery_summ = self.delivery_summ
        o.return_summ = self.return_summ
        o.sms = self.sms
        o.sms_pay_info = self.sms_pay_info
        o.sms_promocode = self.sms_promocode
        o.call_back_email = self.call_back_email
        o.recall_story = self.recall_story
        o.last_call_mark = self.last_call_mark
        o.client_next_call = self.client_next_call
        o.date_of_money_get = self.date_of_money_get if self.date_of_money_get else None

        if self.status in (5, 7):
            o.delivery_cost = 0

        if self.status == 7:
            from datetime import datetime
            o.delivery_day = datetime.now().strftime('%d.%m')

        o.name = self.customer.first_name or o.name
        o.second_name = self.customer.last_name or o.second_name
        o.phone = self.customer.phone or o.phone
        o.email = self.customer.email or o.email
        o.address_full = self.customer.full_address or o.address_full
        o.post_index = self.customer.zip_code or o.post_index
        o.region = self.customer.region or o.region
        o.address = self.customer.street_address or o.address

        o.last_change_time_mark = int(time.time())

        o.save()


class CustomerWrapper:
    def __init__(self, order_wrapper):
        self._order_wrapper = order_wrapper
        self._order = order_wrapper._order
        self.first_name = self._order.name or ''
        self.last_name = self._order.second_name or ''
        self.phone = self._order.phone or ''
        self.email = self._order.email or ''
        self.full_address = self._order.address_full or ''
        self.zip_code = self._order.post_index or ''
        self.region = self._order.region or ''
        self.street_address = self._order.address or ''

    def __str__(self):
        parts = [self.last_name, self.first_name]
        return ' '.join(p for p in parts if p).strip() or 'Без имени'

    @property
    def initials(self):
        first = self.first_name[0] if self.first_name else ''
        last = self.last_name[0] if self.last_name else ''
        return (first + last).upper() or '??'

    def save(self):
        self._order_wrapper._customer_name = self.first_name
        self._order_wrapper._customer_last_name = self.last_name
        self._order_wrapper._customer_phone = self.phone
        self._order_wrapper._customer_email = self.email
        self._order_wrapper._customer_full_address = self.full_address
        self._order_wrapper._customer_zip_code = self.zip_code
        self._order_wrapper._customer_region = self.region
        self._order_wrapper._customer_street_address = self.street_address


class OrderItemsWrapper:
    def __init__(self, crm_order):
        self._order = crm_order

    def all(self):
        items = []
        products = self._order.products.split('::') if self._order.products else []
        qtys = self._order.qty.split('::') if self._order.qty else []
        prices = self._order.prices.split('::') if self._order.prices else []
        colors = self._order.colors.split('::') if self._order.colors else []
        sizes = self._order.sizes.split('::') if self._order.sizes else []

        for i, prod_name in enumerate(products):
            if not prod_name.strip():
                continue
            qty = int(qtys[i]) if i < len(qtys) and qtys[i].strip() else 1
            price = Decimal(prices[i]) if i < len(prices) and prices[i].strip() else Decimal(0)
            color = colors[i] if i < len(colors) else ''
            size = sizes[i] if i < len(sizes) else ''

            items.append(OrderItemWrapper(prod_name.strip(), qty, price, color, size))
        return items

    def count(self):
        return len(self.all())


class OrderItemWrapper:
    def __init__(self, name, quantity, price, color='', size=''):
        self.product_name = name
        self.quantity = quantity
        self.price = price
        self.color = color
        self.size = size
        self.custom_price = None

    @property
    def product(self):
        return ProductProxy(self.product_name, self.price, self.color, self.size)

    @property
    def unit_price(self):
        return self.custom_price if self.custom_price is not None else self.price

    @property
    def total_price(self):
        return self.unit_price * self.quantity


class ProductProxy:
    def __init__(self, name, price, color='', size=''):
        self.name = name
        self.price = price
        self.color = color
        self.size = ''

    def __str__(self):
        return f"{self.name} — ₽{self.price}"


class CategoryProxy:
    def __init__(self, name, products):
        self.name = name
        self._products = products

    @property
    def products(self):
        return self._products


class ProductListProxy:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


def orders_list(request):
    orders_qs = CrmOrder.objects.all().order_by('-date', '-id')

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    amount_from = request.GET.get('amount_from')
    amount_to = request.GET.get('amount_to')
    status = request.GET.get('status')

    if date_from:
        orders_qs = orders_qs.filter(date__gte=date_from)
    if date_to:
        orders_qs = orders_qs.filter(date__lte=date_to)
    if status:
        status_map = {
            'new': 0,
            'collecting': 3,
            'in_transit': 2,
            'delivered': 5,
            'cancelled': 4,
        }
        if status in status_map:
            orders_qs = orders_qs.filter(status=status_map[status])

    paginator = Paginator(orders_qs, 8)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    wrapped_orders = [OrderWrapper(o) for o in page_obj.object_list]

    total_orders = orders_qs.count()
    total_amount_agg = orders_qs.aggregate(total=Sum('order_summ'))['total']
    total_amount = total_amount_agg or 0

    context = {
        'page_obj': page_obj,
        'total_orders': total_orders,
        'total_amount': total_amount,
        'date_from': date_from or '',
        'date_to': date_to or '',
        'amount_from': amount_from or '',
        'amount_to': amount_to or '',
        'status_filter': status or '',
    }
    page_obj.object_list = wrapped_orders
    return render(request, 'dashboard/orders_list.html', context)


def order_detail(request, order_id):
    crm_order = get_object_or_404(CrmOrder, id=order_id)
    order = OrderWrapper(crm_order)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_order':
            order.source = request.POST.get('source', order.source)
            order.order_number = request.POST.get('order_number', order.order_number)
            order.courier_name = request.POST.get('courier_name', order.courier_name)
            delivery_date_str = request.POST.get('delivery_date')
            order.delivery_date = delivery_date_str if delivery_date_str else None
            order.time_restrictions = request.POST.get('time_restrictions', order.time_restrictions)

            status_val = request.POST.get('status')
            if status_val:
                try:
                    order.status = int(status_val)
                except ValueError:
                    pass

            order.customer.first_name = request.POST.get('first_name', order.customer.first_name)
            order.customer.last_name = request.POST.get('last_name', order.customer.last_name)
            order.customer.phone = request.POST.get('phone', order.customer.phone)
            order.customer.email = request.POST.get('email', order.customer.email)
            order.customer.full_address = request.POST.get('full_address', order.customer.full_address)
            order.customer.zip_code = request.POST.get('zip_code', order.customer.zip_code)
            order.customer.region = request.POST.get('region', order.customer.region)
            order.customer.street_address = request.POST.get('street_address', order.customer.street_address)

            order.send_cdek = request.POST.get('send_cdek') == 'on'
            order.cdek_tariff = request.POST.get('cdek_tariff', order.cdek_tariff)

            cdek_length = request.POST.get('cdek_length')
            order.cdek_length = int(cdek_length) if cdek_length else None
            cdek_width = request.POST.get('cdek_width')
            order.cdek_width = int(cdek_width) if cdek_width else None
            cdek_height = request.POST.get('cdek_height')
            order.cdek_height = int(cdek_height) if cdek_height else None
            order.cdek_city = request.POST.get('cdek_city', order.cdek_city)
            order.cdek_city_code = request.POST.get('cdek_city_code', order.cdek_city_code)
            order.cdek_pickup_address = request.POST.get('cdek_pickup_address', order.cdek_pickup_address)
            order.pvz_code = request.POST.get('pvz_code', order.pvz_code)
            order.cdek_address = request.POST.get('cdek_address', order.cdek_address)
            order.cdek_street = request.POST.get('cdek_street', order.cdek_street)
            order.cdek_house = request.POST.get('cdek_house', order.cdek_house)
            order.cdek_apartment = request.POST.get('cdek_apartment', order.cdek_apartment)

            order.delivery_cost_customer = float(request.POST.get('delivery_cost_customer', 0) or 0)
            order.delivery_cost_actual = float(request.POST.get('delivery_cost_actual', 0) or 0)
            order.discount = float(request.POST.get('discount', 0) or 0)
            order.promo_discount = float(request.POST.get('promo_discount', 0) or 0)

            paid_status_val = request.POST.get('paid_status')
            if paid_status_val:
                try:
                    order.paid_status = int(paid_status_val)
                except ValueError:
                    pass

            post_pay_val = request.POST.get('post_pay')
            if post_pay_val:
                try:
                    order.post_pay = int(post_pay_val)
                except ValueError:
                    pass

            order.cashless = 1 if request.POST.get('cashless') == 'on' else 0
            order.office_send = 1 if request.POST.get('office_send') == 'on' else 0

            send_region_val = request.POST.get('send_region')
            if send_region_val:
                try:
                    order.send_region = int(send_region_val)
                except ValueError:
                    pass

            order.delivery_day = request.POST.get('delivery_day', order.delivery_day)
            order.note = request.POST.get('note', order.note)
            order.note_print = request.POST.get('note_print', order.note_print)
            order.way_of_pay_accept = request.POST.get('way_of_pay_accept', order.way_of_pay_accept)

            day_of_pay_accept_str = request.POST.get('day_of_pay_accept')
            if day_of_pay_accept_str:
                from datetime import datetime
                try:
                    order.day_of_pay_accept = datetime.strptime(day_of_pay_accept_str, '%Y-%m-%d').date()
                except ValueError:
                    pass
            else:
                order.day_of_pay_accept = None

            post_status_val = request.POST.get('post_status')
            if post_status_val:
                try:
                    order.post_status = int(post_status_val)
                except ValueError:
                    pass

            order.treck = request.POST.get('treck', order.treck)

            delivery_summ_val = request.POST.get('delivery_summ')
            if delivery_summ_val:
                try:
                    order.delivery_summ = int(delivery_summ_val)
                except ValueError:
                    pass

            return_summ_val = request.POST.get('return_summ')
            if return_summ_val:
                try:
                    order.return_summ = int(return_summ_val)
                except ValueError:
                    pass

            sms_val = request.POST.get('sms')
            order.sms = 1 if sms_val == 'on' else 0

            sms_pay_info_val = request.POST.get('sms_pay_info')
            if sms_pay_info_val:
                try:
                    order.sms_pay_info = int(sms_pay_info_val)
                except ValueError:
                    pass

            sms_promocode_val = request.POST.get('sms_promocode')
            order.sms_promocode = 1 if sms_promocode_val == 'on' else 0

            call_back_email_val = request.POST.get('call_back_email')
            order.call_back_email = 1 if call_back_email_val == 'on' else 0

            order.recall_story = request.POST.get('recall_story', order.recall_story)

            last_call_mark_val = request.POST.get('last_call_mark')
            if last_call_mark_val:
                try:
                    order.last_call_mark = int(last_call_mark_val)
                except ValueError:
                    pass

            client_next_call_val = request.POST.get('client_next_call')
            if client_next_call_val:
                try:
                    order.client_next_call = int(client_next_call_val)
                except ValueError:
                    pass

            date_of_money_get_str = request.POST.get('date_of_money_get')
            if date_of_money_get_str:
                from datetime import datetime
                try:
                    order.date_of_money_get = datetime.strptime(date_of_money_get_str, '%Y-%m-%d').date()
                except ValueError:
                    pass
            else:
                order.date_of_money_get = None

            # Process item quantities and prices from unified form
            products = crm_order.products.split('::') if crm_order.products else []
            qtys = crm_order.qty.split('::') if crm_order.qty else []
            prices = crm_order.prices.split('::') if crm_order.prices else []
            colors = crm_order.colors.split('::') if crm_order.colors else []
            sizes = crm_order.sizes.split('::') if crm_order.sizes else []

            for i in range(len(products)):
                qty_val = request.POST.get(f'item_qty_{i}')
                price_val = request.POST.get(f'item_price_{i}')
                if qty_val and i < len(qtys):
                    qtys[i] = qty_val
                if price_val and i < len(prices):
                    prices[i] = price_val

            # Handle add product
            product_name = request.POST.get('product_name', '').strip()
            product_price = request.POST.get('product_price', '0')
            product_qty = request.POST.get('product_qty', '1')
            if product_name:
                existing_products = '::'.join([p for p in products if p.strip()])
                existing_qtys = '::'.join([q for q in qtys if q.strip()])
                existing_prices = '::'.join([p for p in prices if p.strip()])
                existing_colors = '::'.join([c for c in colors if c.strip()])
                existing_sizes = '::'.join([s for s in sizes if s.strip()])

                sep = '::' if existing_products else ''
                products_list = existing_products + sep + product_name
                qtys_list = existing_qtys + sep + product_qty
                prices_list = existing_prices + sep + product_price
                colors_list = existing_colors + sep + ''
                sizes_list = existing_sizes + sep + ''
            else:
                products_list = '::'.join(products)
                qtys_list = '::'.join(qtys)
                prices_list = '::'.join(prices)
                colors_list = '::'.join(colors)
                sizes_list = '::'.join(sizes)

            crm_order.products = products_list
            crm_order.qty = qtys_list
            crm_order.prices = prices_list
            crm_order.colors = colors_list
            crm_order.sizes = sizes_list
            crm_order.last_change_time_mark = int(time.time())
            crm_order.save()

            try:
                order.save()
                messages.success(request, f'Заказ #{order.id} успешно сохранён')
            except Exception as e:
                error_msg = f'Ошибка сохранения: {str(e)}'
                print(f"SAVE ERROR: {error_msg}")
                print(traceback.format_exc())
                messages.error(request, error_msg)

            return redirect('order_detail', order_id=order.id)

        elif action == 'update_item':
            item_idx = int(request.POST.get('item_idx', 0))
            new_qty = request.POST.get('quantity')
            new_price = request.POST.get('custom_price')

            products = crm_order.products.split('::') if crm_order.products else []
            qtys = crm_order.qty.split('::') if crm_order.qty else []
            prices = crm_order.prices.split('::') if crm_order.prices else []
            colors = crm_order.colors.split('::') if crm_order.colors else []
            sizes = crm_order.sizes.split('::') if crm_order.sizes else []

            if 0 <= item_idx < len(products):
                if new_qty:
                    qtys[item_idx] = new_qty
                if new_price:
                    prices[item_idx] = new_price

            crm_order.products = '::'.join(products)
            crm_order.qty = '::'.join(qtys)
            crm_order.prices = '::'.join(prices)
            crm_order.colors = '::'.join(colors)
            crm_order.sizes = '::'.join(sizes)

            crm_order.last_change_time_mark = int(time.time())
            crm_order.save()
            return redirect('order_detail', order_id=order.id)

        elif action == 'add_item':
            product_name = request.POST.get('product_name', '').strip()
            product_price = request.POST.get('product_price', '0')
            product_qty = request.POST.get('product_qty', '1')

            if product_name:
                existing_products = crm_order.products.rstrip('::') if crm_order.products else ''
                existing_qtys = crm_order.qty.rstrip('::') if crm_order.qty else ''
                existing_prices = crm_order.prices.rstrip('::') if crm_order.prices else ''
                existing_colors = crm_order.colors.rstrip('::') if crm_order.colors else ''
                existing_sizes = crm_order.sizes.rstrip('::') if crm_order.sizes else ''

                sep = '::' if existing_products else ''
                crm_order.products = existing_products + sep + product_name
                crm_order.qty = existing_qtys + sep + product_qty
                crm_order.prices = existing_prices + sep + product_price
                crm_order.colors = existing_colors + sep + ''
                crm_order.sizes = existing_sizes + sep + ''

                crm_order.last_change_time_mark = int(time.time())
                crm_order.save()
            return redirect('order_detail', order_id=order.id)

        elif action == 'remove_item':
            item_idx = int(request.POST.get('item_idx', -1))

            products = crm_order.products.split('::') if crm_order.products else []
            qtys = crm_order.qty.split('::') if crm_order.qty else []
            prices = crm_order.prices.split('::') if crm_order.prices else []
            colors = crm_order.colors.split('::') if crm_order.colors else []
            sizes = crm_order.sizes.split('::') if crm_order.sizes else []

            if 0 <= item_idx < len(products):
                products.pop(item_idx)
                if item_idx < len(qtys):
                    qtys.pop(item_idx)
                if item_idx < len(prices):
                    prices.pop(item_idx)
                if item_idx < len(colors):
                    colors.pop(item_idx)
                if item_idx < len(sizes):
                    sizes.pop(item_idx)

            crm_order.products = '::'.join(products)
            crm_order.qty = '::'.join(qtys)
            crm_order.prices = '::'.join(prices)
            crm_order.colors = '::'.join(colors)
            crm_order.sizes = '::'.join(sizes)

            crm_order.last_change_time_mark = int(time.time())
            crm_order.save()
            return redirect('order_detail', order_id=order.id)

    delivery_dates = []
    today = date.today()
    for i in range(15):
        d = today + timedelta(days=i)
        delivery_dates.append(d)

    product_items = order.items.all()
    product_proxies = [item.product for item in product_items]
    categories = [CategoryProxy('Товары из заказа', ProductListProxy(product_proxies))]
    all_products = product_proxies

    context = {
        'order': order,
        'delivery_dates': delivery_dates,
        'categories': categories,
        'all_products': all_products,
    }
    return render(request, 'dashboard/order_detail.html', context)
