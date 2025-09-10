# serializers.py
from rest_framework import serializers
from .models import User, Category, Shop, ProductInfo, Product, \
    ProductParameter, OrderItem, Order, Contact


class ContactSerializer(serializers.ModelSerializer):
    """
    Сериализатор для контактной информации
    """

    class Meta:
        model = Contact
        fields = ('id', 'city', 'street', 'house', 'structure', 'building',
                  'apartment', 'user', 'phone')
        read_only_fields = ('id',)
        extra_kwargs = {
            'user': {'write_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользователей с вложенными контактами
    """
    contacts = ContactSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'company',
                  'position', 'contacts')
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для категорий товаров
    """

    class Meta:
        model = Category
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class ShopSerializer(serializers.ModelSerializer):
    """
    Сериализатор для магазинов
    """

    class Meta:
        model = Shop
        fields = ('id', 'name', 'state',)
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для продуктов с отображением категории в виде строки
    """
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('name', 'category',)


class ProductParameterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для параметров продуктов
    """
    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value',)


class ProductInfoSerializer(serializers.ModelSerializer):
    """
    Сериализатор для информации о продуктах с вложенными данными
    """
    product = ProductSerializer(read_only=True)  # Вложенный продукт
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'model', 'product', 'shop', 'quantity', 'price',
                  'price_rrc', 'product_parameters',)
        read_only_fields = ('id',)


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для элементов заказа
    """

    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'order',)
        read_only_fields = ('id',)
        extra_kwargs = {
            'order': {'write_only': True}
        }


class OrderItemCreateSerializer(OrderItemSerializer):
    """
    Сериализатор для создания элементов заказа с информацией о продукте
    """
    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    """
    Сериализатор для заказов с вычисляемыми полями
    """
    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)
    total_sum = serializers.IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'state', 'dt', 'total_sum',
                  'contact',)
        read_only_fields = ('id',)
