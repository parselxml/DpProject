# backend/management/commands/import_shop_data.py
import os
import yaml
from django.core.management.base import BaseCommand
from django.db import transaction
from shop.models import Shop, Category, Product, ProductInfo, Parameter, \
    ProductParameter


class Command(BaseCommand):
    help = 'Import shop data from YAML file'

    def add_arguments(self, parser):
        parser.add_argument('file_path',
                            type=str, help='Path to YAML file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        if not os.path.exists(file_path):
            self.stderr.write(
                self.style.ERROR(f'File {file_path} does not exist'))
            return

        self.stdout.write(f'Начинаем импорт из {file_path}')

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Error reading YAML file: {e}'))
            return

        try:
            with transaction.atomic():
                # Создаем или получаем магазин
                shop_name = data['shop']
                shop, created = Shop.objects.get_or_create(name=shop_name)
                self.stdout.write(f'Магазин: {shop_name}')

                # Обрабатываем категории
                for category_data in data['categories']:
                    category, created = Category.objects.get_or_create(
                        id=category_data['id'],
                        defaults={'name': category_data['name']}
                    )
                    category.shops.add(shop)
                    self.stdout.write(f'  Категория: {category.name}')

                # Обрабатываем товары
                for product_data in data['goods']:
                    # Создаем или получаем продукт
                    product, created = Product.objects.get_or_create(
                        name=product_data['name'],
                        category_id=product_data['category']
                    )

                    # Создаем или обновляем информацию о продукте
                    product_info, created = ProductInfo.objects.update_or_create(
                        external_id=product_data['id'],
                        # Важно: передаем external_id
                        shop=shop,
                        product=product,
                        defaults={
                            'model': product_data.get('model', ''),
                            'quantity': product_data['quantity'],
                            'price': product_data['price'],
                            'price_rrc': product_data['price_rrc'],
                        }
                    )

                    self.stdout.write(f'  Товар: {product.name}')

                    # Обрабатываем параметры
                    for param_name, param_value in product_data[
                        'parameters'].items():
                        parameter, created = Parameter.objects.get_or_create(
                            name=param_name)

                        ProductParameter.objects.update_or_create(
                            product_info=product_info,
                            parameter=parameter,
                            defaults={'value': str(param_value)}
                        )

                self.stdout.write(
                    self.style.SUCCESS('Импорт успешно завершен!'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error during import: {e}'))
            raise
