from django.db import models


class ZeroDateField(models.DateField):
    def from_db_value(self, value, expression, connection):
        if value == '0000-00-00':
            return None
        return value

    def get_prep_value(self, value):
        if value == '0000-00-00' or value == '0001-01-01':
            return None
        return super().get_prep_value(value)


class CrmOrder(models.Model):
    id = models.AutoField(primary_key=True)
    source = models.CharField(max_length=30, default='', db_column='source')
    second_name = models.CharField(max_length=50, default='', db_column='second_name')
    name = models.CharField(max_length=50, default='', db_column='name')
    phone = models.CharField(max_length=50, default='', db_column='phone')
    email = models.CharField(max_length=35, default='', db_column='email')
    address_full = models.CharField(max_length=200, default='', db_column='address_full')
    post_index = models.CharField(max_length=20, default='', db_column='post_index')
    region = models.CharField(max_length=100, default='', db_column='region')
    address = models.CharField(max_length=100, default='', db_column='address')
    order_summ = models.IntegerField(default=0, db_column='order_summ')
    discount = models.IntegerField(default=0, db_column='discount')
    promocode = models.CharField(max_length=25, default='', db_column='promocode')
    discount_percent_promocode = models.IntegerField(default=0, db_column='discount_percent_promocode')
    delivery_cost = models.IntegerField(default=300, db_column='delivery_cost')
    order_number = models.CharField(max_length=25, default='', db_column='order_number')
    delivery_summ = models.IntegerField(default=0, db_column='delivery_summ')
    return_summ = models.IntegerField(default=0, db_column='return_summ')
    treck = models.CharField(max_length=25, default='', db_column='treck')
    delivery_date = ZeroDateField(default='0001-01-01', db_column='delivery_date')
    arrival_date = ZeroDateField(default='0001-01-01', db_column='arrival_date')
    post_status = models.IntegerField(default=0, db_column='post_status')
    paid_status = models.IntegerField(default=0, db_column='paid_status')
    next_call_date = ZeroDateField(default='0001-01-01', db_column='next_call_date')
    products = models.CharField(max_length=3000, default='', db_column='products')
    ids_products = models.CharField(max_length=400, default='', db_column='ids_products')
    qty = models.CharField(max_length=300, default='', db_column='qty')
    prices = models.CharField(max_length=400, default='', db_column='prices')
    colors = models.CharField(max_length=800, default='', db_column='colors')
    sizes = models.CharField(max_length=800, default='', db_column='sizes')
    note = models.TextField(default='', db_column='note')
    note_print = models.TextField(default='', db_column='note_print')
    date_timestamp = models.IntegerField(default=0, db_column='date_timestamp')
    id_gift1 = models.IntegerField(default=0, db_column='id_gift1')
    id_gift2 = models.IntegerField(default=0, db_column='id_gift2')
    id_gift3 = models.IntegerField(default=0, db_column='id_gift3')
    id_gift4 = models.IntegerField(default=0, db_column='id_gift4')
    id_gift5 = models.IntegerField(default=0, db_column='id_gift5')
    date = ZeroDateField(db_column='date')
    time = models.TimeField(db_column='time')
    sdek = models.IntegerField(default=0, db_column='sdek')
    status = models.IntegerField(default=0, db_column='status')
    status_print = models.IntegerField(default=0, db_column='status_print')
    send_region = models.IntegerField(default=0, db_column='send_region')
    delivery_day = models.CharField(max_length=10, default='', db_column='delivery_day')
    time_limit = models.CharField(max_length=50, default='', db_column='time_limit')
    cookie_sourse = models.CharField(max_length=200, default='', db_column='cookie_sourse')
    cookie_term = models.CharField(max_length=200, default='', db_column='cookie_term')
    cookie_campaign = models.CharField(max_length=200, default='', db_column='cookie_campaign')
    cookie_content = models.CharField(max_length=200, default='', db_column='cookie_content')
    cookie_time = models.CharField(max_length=200, default='', db_column='cookie_time')
    cookie_php = models.CharField(max_length=500, default='', db_column='cookie_php')
    session_source = models.CharField(max_length=200, default='', db_column='session_source')
    session_term = models.CharField(max_length=200, default='', db_column='session_term')
    session_campaign = models.CharField(max_length=200, default='', db_column='session_campaign')
    session_content = models.CharField(max_length=200, default='', db_column='session_content')
    session_time = models.CharField(max_length=200, default='', db_column='session_time')
    session_php = models.CharField(max_length=500, default='', db_column='session_php')
    current_utm_source = models.CharField(max_length=200, default='', db_column='current_utm_source')
    current_utm_term = models.CharField(max_length=200, default='', db_column='current_utm_term')
    current_utm_campaign = models.CharField(max_length=200, default='', db_column='current_utm_campaign')
    current_utm_content = models.CharField(max_length=200, default='', db_column='current_utm_content')
    current_utm_time = models.CharField(max_length=200, default='', db_column='current_utm_time')
    current_utm_php = models.CharField(max_length=500, default='', db_column='current_utm_php')
    delivery_way = models.CharField(max_length=100, default='', db_column='delivery_way')
    sms = models.IntegerField(default=0, db_column='sms')
    call_back_email = models.IntegerField(default=0, db_column='call_back_email')
    post_pay = models.IntegerField(default=1, db_column='post_pay')
    sms_pay_info = models.IntegerField(default=0, db_column='sms_pay_info')
    sms_promocode = models.IntegerField(default=0, db_column='sms_promocode')
    delivery_expenses = models.IntegerField(default=250, db_column='delivery_expenses')
    day_of_pay_accept = ZeroDateField(default='0001-01-01', db_column='day_of_pay_accept')
    way_of_pay_accept = models.CharField(max_length=50, default='', db_column='way_of_pay_accept')
    cashless = models.IntegerField(default=0, db_column='cashless')
    office_send = models.IntegerField(default=1, db_column='office_send')
    curier_name = models.CharField(max_length=50, default='', db_column='curier_name')
    last_call_mark = models.IntegerField(default=0, db_column='last_call_mark')
    recall_story = models.CharField(max_length=7000, default='', db_column='recall_story')
    client_next_call = models.IntegerField(default=0, db_column='client_next_call')
    date_of_money_get = ZeroDateField(default='0001-01-01', db_column='date_of_money_get')
    cdek_city_code = models.CharField(max_length=10, default='', db_column='cdek_city_code')
    cdek_city_name = models.CharField(max_length=100, default='', db_column='cdek_city_name')
    pvz_code = models.CharField(max_length=10, default='', db_column='pvz_code')
    pvz_address = models.CharField(max_length=120, default='', db_column='pvz_address')
    cdek_address = models.CharField(max_length=250, default='', db_column='cdek_address')
    cdek_tariff_code = models.CharField(max_length=5, default='', db_column='cdek_tariff_code')
    cdek_sizes_package = models.CharField(max_length=20, default='', db_column='cdek_sizes_package')
    cdek_client_address = models.CharField(max_length=250, default='', db_column='cdek_client_address')
    last_change_time_mark = models.IntegerField(default=0, db_column='last_change_time_mark')

    class Meta:
        db_table = 'crm'
        managed = False
        ordering = ['-date', '-id']

    def __str__(self):
        return f"#{self.order_number or self.id}"

    @property
    def status_label(self):
        labels = {
            0: 'Новый',
            1: 'Отзыв',
            2: 'Подтверждён',
            3: 'В обработке',
            4: 'Отменён',
            5: 'Самовывоз',
            6: 'Отложен',
            7: 'Самовывоз собран',
            8: 'Приход',
            9: 'Расход',
        }
        return labels.get(self.status, 'Неизвестно')

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
    def customer_name(self):
        parts = [self.second_name, self.name]
        return ' '.join(p for p in parts if p).strip() or 'Без имени'

    @property
    def initials(self):
        first = self.name[0] if self.name else ''
        last = self.second_name[0] if self.second_name else ''
        return (first + last).upper() or '??'

    @property
    def total_amount(self):
        try:
            price_list = [float(p) for p in self.prices.split('::') if p.strip()]
            qty_list = [int(q) for q in self.qty.split('::') if q.strip()]
            total = sum(p * q for p, q in zip(price_list, qty_list))
            return total
        except (ValueError, ZeroDivisionError):
            return 0

    @property
    def product_list(self):
        if self.products:
            return [p.strip() for p in self.products.split('::') if p.strip()]
        return []

    @property
    def send_cdek(self):
        return self.sdek == 1

    @property
    def cdek_tariff(self):
        return self.cdek_tariff_code or ''


class Recall(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default='', db_column='name')
    phone = models.CharField(max_length=50, default='', db_column='phone')
    note = models.TextField(default='', db_column='note')
    status = models.IntegerField(default=0, db_column='status')

    class Meta:
        db_table = 'recall'
        managed = False

    def __str__(self):
        return f"{self.name} - {self.phone}"


class FbForm(models.Model):
    id = models.AutoField(primary_key=True)
    source = models.CharField(max_length=100, default='', db_column='source')
    name = models.CharField(max_length=100, default='', db_column='name')
    contact = models.CharField(max_length=200, default='', db_column='contact')
    note = models.TextField(default='', db_column='note')
    check_status = models.IntegerField(default=0, db_column='check')
    date = ZeroDateField(db_column='date')
    time = models.TimeField(db_column='time')
    cookie_sourse = models.CharField(max_length=100, default='', db_column='cookie_sourse')
    cookie_term = models.CharField(max_length=200, default='', db_column='cookie_term')
    cookie_campaign = models.CharField(max_length=200, default='', db_column='cookie_campaign')

    class Meta:
        db_table = 'fb_form'
        managed = False

    def __str__(self):
        return f"{self.name} - {self.contact}"
