# views.py
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from requests import get
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from ujson import loads as load_json
from yaml import load as load_yaml, Loader

from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact, ConfirmEmailToken
from .serializers import UserSerializer, CategorySerializer, ShopSerializer, ProductInfoSerializer, \
    OrderItemSerializer, OrderSerializer, ContactSerializer
from .signals import order_created


class BaseAPIView(APIView):
    """
    Базовый класс для API views с общими методами
    """

    def check_authentication(self, request):
        """
        Проверка аутентификации пользователя
        """
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Требуется авторизация'}, status=403)
        return None

    def check_shop_permission(self, request):
        """
        Проверка прав доступа для магазинов
        """
        auth_check = self.check_authentication(request)
        if auth_check:
            return auth_check

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Доступно только для магазинов'}, status=403)
        return None

    def validate_required_fields(self, data, required_fields):
        """
        Валидация обязательных полей
        """
        if not required_fields.issubset(data):
            return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})
        return None


class RegisterAccount(APIView):
    """
    Контроллер для регистрации новых пользователей
    """

    def post(self, request, *args, **kwargs):
        """
        Обработка POST запроса для создания нового пользователя
        """
        # Проверяем наличие всех обязательных полей
        required_fields = {'first_name', 'last_name', 'email', 'password', 'company', 'position'}
        if not required_fields.issubset(request.data):
            return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

        # Валидация сложности пароля
        try:
            validate_password(request.data['password'])
        except ValidationError as password_error:
            error_messages = [str(error) for error in password_error.error_list]
            return JsonResponse({'Status': False, 'Errors': {'password': error_messages}})
        except Exception as password_error:
            return JsonResponse({'Status': False, 'Errors': {'password': [str(password_error)]}})

        # Проверяем и сохраняем данные пользователя
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            user.set_password(request.data['password'])
            user.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': user_serializer.errors})

class ConfirmAccount(APIView):
    """
    Контроллер для подтверждения email адреса
    """

    def post(self, request, *args, **kwargs):
        """
        Подтверждение email через токен
        """
        if not {'email', 'token'}.issubset(request.data):
            return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

        # Поиск и проверка токена подтверждения
        token = ConfirmEmailToken.objects.filter(
            user__email=request.data['email'],
            key=request.data['token']
        ).first()

        if token:
            token.user.is_active = True
            token.user.save()
            token.delete()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': 'Неправильно указан токен или email'})


class AccountDetails(BaseAPIView):
    """
    Контроллер для управления данными аккаунта пользователя
    """

    def post(self, request, *args, **kwargs):
        """
        Обновление данных пользователя
        """
        auth_check = self.check_authentication(request)
        if auth_check:
            return auth_check

        # Обработка изменения пароля
        if 'password' in request.data:
            try:
                validate_password(request.data['password'])
            except ValidationError as password_error:
                error_messages = [str(error) for error in password_error.error_list]
                return JsonResponse({'Status': False, 'Errors': {'password': error_messages}})
            except Exception as password_error:
                return JsonResponse({'Status': False, 'Errors': {'password': [str(password_error)]}})
            else:
                request.user.set_password(request.data['password'])

        # Обновление остальных данных
        user_serializer = UserSerializer(request.user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': user_serializer.errors})


class LoginAccount(APIView):
    """
    Контроллер для авторизации пользователей
    """

    def post(self, request, *args, **kwargs):
        """
        Аутентификация пользователя
        """
        if not {'email', 'password'}.issubset(request.data):
            return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'})

        user = authenticate(request, username=request.data['email'], password=request.data['password'])

        if user is not None and user.is_active:
            token, _ = Token.objects.get_or_create(user=user)
            return JsonResponse({'Status': True, 'Token': token.key})

        return JsonResponse({'Status': False, 'Errors': 'Ошибка авторизации'})


class CategoryView(ListAPIView):
    """
    Контроллер для просмотра категорий товаров
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    """
    Контроллер для просмотра активных магазинов
    """
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class ProductInfoView(APIView):
    """
    Контроллер для поиска и фильтрации товаров
    """

    def get(self, request: Request, *args, **kwargs):
        """
        Поиск товаров с фильтрацией по магазину и категории
        """
        # Базовый запрос для активных магазинов
        query = Q(shop__state=True)

        # Фильтрация по магазину
        shop_id = request.query_params.get('shop_id')
        if shop_id:
            query &= Q(shop_id=shop_id)

        # Фильтрация по категории
        category_id = request.query_params.get('category_id')
        if category_id:
            query &= Q(product__category_id=category_id)

        # Выполнение запроса с оптимизацией
        queryset = ProductInfo.objects.filter(query).select_related(
            'shop', 'product__category'
        ).prefetch_related(
            'product_parameters__parameter'
        ).distinct()

        serializer = ProductInfoSerializer(queryset, many=True)
        return Response(serializer.data)


class ProductDetailView(APIView):
    """
    Контроллер для получения детальной информации о конкретном товаре
    """

    def get(self, request, pk, *args, **kwargs):
        """
        Получение детальной информации о товаре по ID
        """
        if not request.user.is_authenticated:
            return JsonResponse(
                {'Status': False, 'Error': 'Требуется авторизация'},
                status=403
            )

        try:
            # Ищем конкретный товар по ID
            product_info = ProductInfo.objects.filter(
                Q(shop__state=True) & Q(id=pk)
            ).select_related(
                'product__category', 'shop'
            ).prefetch_related(
                'product_parameters__parameter'
            ).first()

            if not product_info:
                return JsonResponse(
                    {'Status': False, 'Error': 'Товар не найден'},
                    status=404
                )

            # Сериализуем данные
            serializer = ProductInfoSerializer(product_info)
            return Response(serializer.data)

        except Exception as e:
            return JsonResponse(
                {'Status': False, 'Error': str(e)},
                status=500
            )


class BasketView(BaseAPIView):
    """
    Контроллер для управления корзиной покупок
    """

    def get(self, request, *args, **kwargs):
        """
        Получение содержимого корзины пользователя
        """
        auth_check = self.check_authentication(request)
        if auth_check:
            return auth_check

        basket = Order.objects.filter(
            user_id=request.user.id, state='basket'
        ).prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter'
        ).annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))
        ).distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Добавление товаров в корзину
        """
        auth_check = self.check_authentication(request)
        if auth_check:
            return auth_check

        items_string = request.data.get('items')
        if not items_string:
            return JsonResponse({'Status': False, 'Errors': 'Не указаны товары для добавления'})

        try:
            items_dict = load_json(items_string)
        except ValueError:
            return JsonResponse({'Status': False, 'Errors': 'Неверный формат данных'})

        # Получение или создание корзины
        basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
        created_count = 0

        for item_data in items_dict:
            item_data['order'] = basket.id
            serializer = OrderItemSerializer(data=item_data)

            if serializer.is_valid():
                try:
                    serializer.save()
                    created_count += 1
                except IntegrityError as error:
                    return JsonResponse({'Status': False, 'Errors': str(error)})
            else:
                return JsonResponse({'Status': False, 'Errors': serializer.errors})

        return JsonResponse({'Status': True, 'Создано объектов': created_count})

    def delete(self, request, *args, **kwargs):
        """
        Удаление товаров из корзины
        """
        auth_check = self.check_authentication(request)
        if auth_check:
            return auth_check

        # Пробуем получить из параметров URL
        items_string = request.GET.get('items')

        # Если нет в URL, пробуем из тела запроса
        if not items_string:
            items_string = request.data.get('items')

        if not items_string:
            return JsonResponse({'Status': False, 'Errors': 'Не указаны товары для удаления'})

        items_list = items_string.split(',')
        basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')

        # Формирование условия для удаления
        delete_query = Q()
        valid_items = False

        for item_id in items_list:
            if item_id.isdigit():
                delete_query |= Q(order_id=basket.id, id=item_id)
                valid_items = True

        if valid_items:
            deleted_count = OrderItem.objects.filter(delete_query).delete()[0]
            return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})

        return JsonResponse({'Status': False, 'Errors': 'Неверный формат идентификаторов'})

    def put(self, request, *args, **kwargs):
        """
        Обновление количества товаров в корзине
        """
        auth_check = self.check_authentication(request)
        if auth_check:
            return auth_check

        items_string = request.data.get('items')
        if not items_string:
            return JsonResponse({'Status': False, 'Errors': 'Не указаны товары для обновления'})

        try:
            items_dict = load_json(items_string)
        except ValueError:
            return JsonResponse({'Status': False, 'Errors': 'Неверный формат данных'})

        basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
        updated_count = 0

        for item_data in items_dict:
            if (isinstance(item_data.get('id'), int) and
                    isinstance(item_data.get('quantity'), int)):
                updated_count += OrderItem.objects.filter(
                    order_id=basket.id, id=item_data['id']
                ).update(quantity=item_data['quantity'])

        return JsonResponse({'Status': True, 'Обновлено объектов': updated_count})


class PartnerUpdate(BaseAPIView):
    """
    Контроллер для обновления прайс-листов партнеров
    """

    def post(self, request, *args, **kwargs):
        """
        Обновление данных магазина из YAML файла
        """
        permission_check = self.check_shop_permission(request)
        if permission_check:
            return permission_check

        url = request.data.get('url')
        if not url:
            return JsonResponse({'Status': False, 'Errors': 'Не указан URL прайс-листа'})

        # Валидация URL
        validate_url = URLValidator()
        try:
            validate_url(url)
        except ValidationError as e:
            return JsonResponse({'Status': False, 'Error': str(e)})

        try:
            # Загрузка и обработка YAML данных
            stream = get(url).content
            data = load_yaml(stream, Loader=Loader)

            # Создание или обновление магазина
            shop, _ = Shop.objects.get_or_create(
                name=data['shop'],
                user_id=request.user.id
            )

            # Обработка категорий
            for category_data in data['categories']:
                category, _ = Category.objects.get_or_create(
                    id=category_data['id'],
                    name=category_data['name']
                )
                category.shops.add(shop.id)
                category.save()

            # Очистка старых данных и добавление новых товаров
            ProductInfo.objects.filter(shop_id=shop.id).delete()

            for product_data in data['goods']:
                product, _ = Product.objects.get_or_create(
                    name=product_data['name'],
                    category_id=product_data['category']
                )

                product_info = ProductInfo.objects.create(
                    product_id=product.id,
                    external_id=product_data['id'],
                    model=product_data['model'],
                    price=product_data['price'],
                    price_rrc=product_data['price_rrc'],
                    quantity=product_data['quantity'],
                    shop_id=shop.id
                )

                # Обработка параметров товара
                for param_name, param_value in product_data['parameters'].items():
                    parameter, _ = Parameter.objects.get_or_create(name=param_name)
                    ProductParameter.objects.create(
                        product_info_id=product_info.id,
                        parameter_id=parameter.id,
                        value=param_value
                    )

            return JsonResponse({'Status': True})

        except Exception as e:
            return JsonResponse({'Status': False, 'Errors': str(e)})


class PartnerState(BaseAPIView):
    """
    Контроллер для управления статусом магазина
    """

    def get(self, request, *args, **kwargs):
        """
        Получение текущего статуса магазина
        """
        permission_check = self.check_shop_permission(request)
        if permission_check:
            return permission_check

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Изменение статуса магазина
        """
        permission_check = self.check_shop_permission(request)
        if permission_check:
            return permission_check

        state = request.data.get('state')
        if state is None:
            return JsonResponse({'Status': False, 'Errors': 'Не указан статус'})

        try:
            bool_state = state.lower() in ('true', '1', 'yes', 'on')
            Shop.objects.filter(user_id=request.user.id).update(state=bool_state)
            return JsonResponse({'Status': True})
        except Exception as error:
            return JsonResponse({'Status': False, 'Errors': str(error)})


class PartnerOrders(BaseAPIView):
    """
    Контроллер для получения заказов партнера
    """

    def get(self, request, *args, **kwargs):
        """
        Получение заказов связанных с магазином пользователя
        """
        permission_check = self.check_shop_permission(request)
        if permission_check:
            return permission_check

        # Получение заказов с аннотацией общей суммы
        orders = Order.objects.filter(
            ordered_items__product_info__shop__user_id=request.user.id
        ).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter'
        ).select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))
        ).distinct()

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class ContactView(BaseAPIView):
    """
    Контроллер для управления контактной информацией
    """

    def get(self, request, *args, **kwargs):
        """
        Получение контактов пользователя
        """
        auth_check = self.check_authentication(request)
        if auth_check:
            return auth_check

        contacts = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Создание нового контакта
        """
        auth_check = self.check_authentication(request)
        if auth_check:
            return auth_check

        # Проверяем обязательные поля
        required_fields = {'city', 'street', 'phone'}
        if not required_fields.issubset(request.data):
            return JsonResponse({
                'Status': False,
                'Errors': 'Не указаны все необходимые аргументы'
            })

        try:
            # Создаем копию данных и добавляем user_id
            from django.http import QueryDict
            request_data = request.data.copy()
            if hasattr(request_data, '_mutable'):
                request_data._mutable = True
            request_data['user'] = request.user.id

            serializer = ContactSerializer(data=request_data)

            if serializer.is_valid():
                serializer.save()
                return JsonResponse({'Status': True})
            else:
                return JsonResponse({
                    'Status': False,
                    'Errors': serializer.errors
                })

        except Exception as e:
            import traceback
            print(f" Ошибка при создании контакта: {str(e)}")
            print(f" Traceback: {traceback.format_exc()}")
            return JsonResponse({
                'Status': False,
                'Errors': 'Внутренняя ошибка сервера'
            }, status=500)

    def delete(self, request, *args, **kwargs):
        """
        Удаление контактов
        """
        auth_check = self.check_authentication(request)
        if auth_check:
            return auth_check

        items_string = request.data.get('items')
        if not items_string:
            return JsonResponse({'Status': False, 'Errors': 'Не указаны контакты для удаления'})

        items_list = items_string.split(',')
        delete_query = Q()
        valid_items = False

        for contact_id in items_list:
            if contact_id.isdigit():
                delete_query |= Q(user_id=request.user.id, id=contact_id)
                valid_items = True

        if valid_items:
            deleted_count = Contact.objects.filter(delete_query).delete()[0]
            return JsonResponse({'Status': True, 'Удалено объектов': deleted_count})

        return JsonResponse({'Status': False, 'Errors': 'Неверный формат идентификаторов'})

    def put(self, request, *args, **kwargs):
        """
        Обновление контактной информации
        """
        auth_check = self.check_authentication(request)
        if auth_check:
            return auth_check

        if 'id' not in request.data or not request.data['id'].isdigit():
            return JsonResponse({'Status': False, 'Errors': 'Не указан корректный ID контакта'})

        contact = Contact.objects.filter(
            id=request.data['id'],
            user_id=request.user.id
        ).first()

        if not contact:
            return JsonResponse({'Status': False, 'Errors': 'Контакт не найден'})

        serializer = ContactSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'Status': True})
        else:
            return JsonResponse({'Status': False, 'Errors': serializer.errors})


class OrderView(BaseAPIView):
    """
    Контроллер для управления заказами пользователя
    """

    def get(self, request, *args, **kwargs):
        """
        Получение истории заказов пользователя
        """
        auth_check = self.check_authentication(request)
        if auth_check:
            return auth_check

        orders = Order.objects.filter(
            user_id=request.user.id
        ).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter'
        ).select_related('contact').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'))
        ).distinct()

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Оформление заказа из корзины
        """
        auth_check = self.check_authentication(request)
        if auth_check:
            return auth_check

        try:
            print(f"🔍 DEBUG Order data: {request.data}")

            if not {'id', 'contact'}.issubset(request.data):
                return JsonResponse({
                    'Status': False,
                    'Errors': 'Не указаны все необходимые аргументы'
                })

            order_id = request.data['id']
            contact_id = request.data['contact']

            # Проверяем существование заказа и контакта
            try:
                order = Order.objects.get(id=order_id, user_id=request.user.id, state='basket')
                contact = Contact.objects.get(id=contact_id, user_id=request.user.id)
            except Order.DoesNotExist:
                return JsonResponse({
                    'Status': False,
                    'Errors': 'Заказ не найден'
                })
            except Contact.DoesNotExist:
                return JsonResponse({
                    'Status': False,
                    'Errors': 'Контакт не найден'
                })

            # Обновляем заказ
            order.contact = contact
            order.state = 'new'
            order.save()

            # Отправляем сигнал о новом заказе
            order_created.send(sender=self.__class__, user_id=request.user.id)

            return JsonResponse({'Status': True})

        except IntegrityError as e:
            print(f"❌ IntegrityError: {e}")
            return JsonResponse({
                'Status': False,
                'Errors': 'Ошибка базы данных'
            })
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            print(f"🔍 Traceback: {traceback.format_exc()}")
            return JsonResponse({
                'Status': False,
                'Errors': 'Внутренняя ошибка сервера'
            }, status=500)