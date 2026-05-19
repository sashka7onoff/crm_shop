# Реализация сохранения изменений в заказе

## Что было сделано

Кнопка **"Сохранить изменения"** в карточке заказа (`order_detail.html`) теперь сохраняет все поля заказа в БД, аналогично оригинальному PHP CRM (`add_update_crm.php`).

## Изменённые файлы

### 1. `dashboard/views.py`

#### OrderWrapper.__init__ — добавлены поля:
- `order_number` — номер заказа
- `cdek_city_code` — код города СДЭК
- `pvz_code` — код ПВЗ
- `cdek_address` — адрес клиента СДЭК
- `paid_status` — статус оплаты (0/1)
- `post_pay` — тип оплаты (0=предоплата не оплачена, 1=наложенный платёж, 2=предоплата оплачена)
- `cashless` — безналичный расчёт (0/1)
- `office_send` — отправка из офиса (0/1)
- `send_region` — регион отправки (0=не определён, 1=Москва, 2=Регионы)
- `delivery_day` — дата доставки (текст)
- `note` — внутренняя заметка
- `note_print` — заметка для печати
- `way_of_pay_accept` — способ получения оплаты
- `day_of_pay_accept` — дата получения предоплаты
- `post_status` — статус почты (0-8)
- `treck` — трек-номер
- `delivery_summ` — сумма доставки
- `return_summ` — сумма возврата
- `sms` — СМС с треком отправлено (0/1)
- `sms_pay_info` — статус СМС с оплатой (0-9)
- `sms_promocode` — СМС с промокодом (0/1)
- `call_back_email` — обратный звонок email (0/1)
- `recall_story` — история звонков
- `last_call_mark` — timestamp последнего звонка
- `client_next_call` — timestamp следующего звонка
- `date_of_money_get` — дата получения денег

#### OrderWrapper.save() — добавлена логика:
- Сохранение всех новых полей в БД
- **Автоматическая установка `delivery_cost=0`** при статусе 5 (Самовывоз) или 7 (Самовывоз собран) — как в PHP CRM
- **Автоматическая установка `delivery_day=сегодня`** при статусе 7 — как в PHP CRM
- Установка `last_change_time_mark` при каждом сохранении

#### order_detail() view — добавлена обработка POST:
- Все новые поля из формы обрабатываются и передаются в wrapper
- Валидация числовых полей через try/except
- Конвертация дат из строки в date объекты

### 2. `dashboard/templates/dashboard/order_detail.html`

#### Добавлены секции:
1. **Регион отправки** — select (Москва/Регионы), статус почты, трек-номер
2. **Оплата** — статус оплаты, тип оплаты, дата получения предоплаты, способ оплаты, дата получения денег, сумма доставки, чекбоксы безналичный/офис
3. **СМС уведомления** — чекбоксы СМС с треком/промокодом/email, статус СМС с оплатой
4. **Заметки** — внутренняя заметка, заметка для печати, история звонков, timestamps, сумма возврата
5. **Имя/Фамилия** — теперь редактируемые (были disabled)

#### Расширена секция СДЭК:
- Код города СДЭК
- Код ПВЗ
- Адрес клиента СДЭК

## Соответствие PHP CRM

| PHP CRM (add_update_crm.php) | Python CRM (views.py) | Статус |
|------------------------------|----------------------|--------|
| UPDATE crm SET ... 30+ полей | o.save() — 30+ полей | Реализовано |
| delivery_cost=0 при status 5,7 | if self.status in (5, 7) | Реализовано |
| delivery_day=сегодня при status 7 | if self.status == 7 | Реализовано |
| last_change_time_mark | o.last_change_time_mark | Реализовано |
| recall_story при status 1 | Через форму (recall_story) | Реализовано |
| client_next_call | Через форму (client_next_call) | Реализовано |

## Поля БД crm, которые сохраняются

| Поле | Описание |
|------|----------|
| source | Источник/магазин |
| order_number | Номер заказа |
| curier_name | Имя курьера |
| delivery_date | Дата доставки (date) |
| delivery_day | Дата доставки (текст) |
| time_limit | Временные ограничения |
| status | Статус заказа |
| sdek | Отправка СДЭК |
| cdek_tariff_code | Тариф СДЭК |
| cdek_city_code | Код города СДЭК |
| cdek_city_name | Город СДЭК |
| pvz_code | Код ПВЗ |
| pvz_address | Адрес ПВЗ |
| cdek_address | Адрес клиента СДЭК |
| cdek_client_address | Адрес клиента (формат ::) |
| cdek_sizes_package | Размеры упаковки (формат ::) |
| delivery_cost | Стоимость доставки для клиента |
| delivery_expenses | Затраты на доставку |
| discount | Скидка |
| discount_percent_promocode | Скидка по промокоду |
| paid_status | Статус оплаты |
| post_pay | Тип оплаты |
| cashless | Безналичный расчёт |
| office_send | Отправка из офиса |
| send_region | Регион отправки |
| post_status | Статус почты |
| treck | Трек-номер |
| delivery_summ | Сумма доставки |
| return_summ | Сумма возврата |
| sms | СМС с треком |
| sms_pay_info | СМС с оплатой |
| sms_promocode | СМС с промокодом |
| call_back_email | Обратный звонок email |
| way_of_pay_accept | Способ оплаты |
| day_of_pay_accept | Дата получения предоплаты |
| date_of_money_get | Дата получения денег |
| note | Внутренняя заметка |
| note_print | Заметка для печати |
| recall_story | История звонков |
| last_call_mark | Последний звонок (timestamp) |
| client_next_call | Следующий звонок (timestamp) |
| name | Имя клиента |
| second_name | Фамилия клиента |
| phone | Телефон |
| email | Email |
| address_full | Полный адрес |
| post_index | Индекс |
| region | Регион |
| address | Адрес |
| last_change_time_mark | Время последнего изменения |
