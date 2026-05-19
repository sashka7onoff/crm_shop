from django.core.management.base import BaseCommand
from datetime import date, timedelta
import random
from dashboard.models import Customer, Product, ProductCategory, Order, OrderItem


class Command(BaseCommand):
    help = 'Seed database with test orders data'

    def handle(self, *args, **kwargs):
        customers_data = [
            ('Игорь', 'Лебедев'),
            ('Анна', 'Поляк'),
            ('Алина', 'Кузьмина'),
            ('Павел', 'Зайцев'),
            ('Светлана', 'Ким'),
            ('Роман', 'Волков'),
            ('Мария', 'Соколова'),
            ('Дмитрий', 'Новиков'),
            ('Елена', 'Морозова'),
            ('Алексей', 'Петров'),
            ('Ольга', 'Иванова'),
            ('Сергей', 'Козлов'),
            ('Наталья', 'Сидорова'),
            ('Андрей', 'Попов'),
            ('Татьяна', 'Белова'),
        ]

        categories_data = [
            'Взрослые зверошапки',
            'Короткие с помпонами',
            'Ушанки',
            'Подростковые',
            'Детские',
            'Повязки',
            'Гетры',
            'Варежки',
            'Муфты',
            'Хвосты',
        ]

        products_data = {
            'Взрослые зверошапки': [
                ('Шапка «Полярная лиса»', 4500),
                ('Шапка «Норка»', 5600),
                ('Шапка «Енот»', 3500),
                ('Шапка «Песец»', 5200),
                ('Шапка «Волк»', 4800),
                ('Шапка «Лисица»', 4200),
            ],
            'Короткие с помпонами': [
                ('Ушанка с помпоном «Баргузинский соболь»', 6800),
                ('Шапка с помпоном «Мурманск»', 3900),
                ('Шапка с помпоном «Арктика»', 4100),
                ('Ушанка с помпоном «Тундра»', 5500),
            ],
            'Ушанки': [
                ('Ушанка «Сибирь»', 6800),
                ('Ушанка «Буран»', 5900),
                ('Ушанка «Тайга»', 6200),
                ('Ушанка «Морозко»', 7200),
            ],
            'Подростковые': [
                ('Шапка подростковая «Лисёнок»', 2800),
                ('Шапка подростковая «Зайчонок»', 2600),
                ('Ушанка подростковая «Снежок»', 3400),
            ],
            'Детские': [
                ('Шапка детская «Мишутка»', 2200),
                ('Шапка детская «Зайка»', 2000),
                ('Шапка детская «Лисичка»', 2400),
                ('Ушанка детская «Пингвин»', 2800),
            ],
            'Повязки': [
                ('Повязка «Классика»', 1500),
                ('Повязка «Меховая»', 1800),
                ('Повязка «Стиль»', 1600),
            ],
            'Гетры': [
                ('Гетры «Тёплые»', 1900),
                ('Гетры «Меховые»', 2200),
            ],
            'Варежки': [
                ('Варежки «Классика»', 1900),
                ('Варежки «Меховые»', 2400),
                ('Варежки «Детские»', 1500),
            ],
            'Муфты': [
                ('Муфта «Элегант»', 2800),
                ('Муфта «Классика»', 2400),
            ],
            'Хвосты': [
                ('Хвост «Лисий»', 1200),
                ('Хвост «Волчий»', 1400),
                ('Хвост «Заячий»', 1000),
            ],
        }

        statuses = ['new', 'collecting', 'in_transit', 'delivered', 'cancelled']
        status_weights = [15, 25, 20, 30, 10]

        customers = []
        for first, last in customers_data:
            c, _ = Customer.objects.get_or_create(first_name=first, last_name=last)
            customers.append(c)

        categories = {}
        for cat_name in categories_data:
            cat, _ = ProductCategory.objects.get_or_create(name=cat_name)
            categories[cat_name] = cat

        products = []
        for cat_name, items in products_data.items():
            category = categories[cat_name]
            for name, price in items:
                p, _ = Product.objects.get_or_create(
                    name=name,
                    defaults={'price': price, 'category': category}
                )
                if not p.category:
                    p.category = category
                    p.save()
                products.append(p)

        Order.objects.all().delete()
        OrderItem.objects.all().delete()

        for i in range(64):
            days_ago = random.randint(0, 90)
            order_date = date.today() - timedelta(days=days_ago)
            customer = random.choice(customers)
            status = random.choices(statuses, weights=status_weights, k=1)[0]

            num_items = random.randint(1, 4)
            selected_products = random.sample(products, num_items)

            total = 0
            order = Order.objects.create(
                customer=customer,
                date=order_date,
                total_amount=0,
                status=status,
            )

            for product in selected_products:
                qty = random.randint(1, 3)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                )
                total += product.price * qty

            order.total_amount = total
            order.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully created 64 orders with {len(products)} products'))
