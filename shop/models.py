# models.py
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.tokens import get_token_generator


class UserManager(BaseUserManager):
    """Кастомный менеджер для модели User"""

    def create_user(self, email, password=None, **extra_fields):
        #Создание обычного пользователя
        if not email:
            raise ValueError('Email является обязательным полем')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        #Создание суперпользователя
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff'):
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        if extra_fields.get('is_superuser'):
            raise ValueError('Суперпользователь должен иметь is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Модель пользователя системы"""

    USER_TYPE_CHOICES = (
        ('shop', 'Магазин'),
        ('buyer', 'Покупатель'),
    )

    username = None
    email = models.EmailField(_('email address'), unique=True)
    company = models.CharField('Компания', max_length=40, blank=True)
    position = models.CharField('Должность', max_length=40, blank=True)
    type = models.CharField('Тип пользователя', choices=USER_TYPE_CHOICES, max_length=5, default='buyer')
    is_active = models.BooleanField('Активный', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)

    def __str__(self):
        return f'{self.email} ({self.get_full_name()})'


class Shop(models.Model):
    #Модель магазина

    name = models.CharField('Название', max_length=50)
    url = models.URLField('Ссылка', null=True, blank=True)
    user = models.OneToOneField(User, verbose_name='Владелец',
                                on_delete=models.CASCADE, null=True, blank=True)
    state = models.BooleanField('Статус заказов', default=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    #Модель категории товаров

    name = models.CharField('Название', max_length=40)
    shops = models.ManyToManyField(Shop, verbose_name='Магазины',
                                   related_name='categories', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    #Модель продукта

    name = models.CharField('Название', max_length=80)
    category = models.ForeignKey(Category, verbose_name='Категория',
                                 related_name='products', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.category})'


# backend/models.py
class ProductInfo(models.Model):
    objects = models.manager.Manager()
    model = models.CharField(max_length=80, verbose_name='Модель', blank=True)
    external_id = models.PositiveIntegerField(verbose_name='Внешний ИД')
    product = models.ForeignKey(Product, verbose_name='Продукт', related_name='product_infos', blank=True,
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='product_infos', blank=True,
                             on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Рекомендуемая розничная цена')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = "Информационный список о продуктах"
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'external_id'], name='unique_product_info'),
        ]


class Parameter(models.Model):
    #Модель параметра товара

    name = models.CharField('Название', max_length=40)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    #Модель связи параметра с продуктом

    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте',
                                     related_name='product_parameters', on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name='Параметр',
                                  related_name='product_parameters', on_delete=models.CASCADE)
    value = models.CharField('Значение', max_length=100)

    class Meta:
        verbose_name = 'Параметр продукта'
        verbose_name_plural = 'Параметры продуктов'
        constraints = [
            models.UniqueConstraint(
                fields=['product_info', 'parameter'],
                name='unique_product_parameter'
            ),
        ]

    def __str__(self):
        return f'{self.parameter}: {self.value}'


class Contact(models.Model):
    #Модель контактной информации пользователя

    user = models.ForeignKey(User, verbose_name='Пользователь',
                             related_name='contacts', on_delete=models.CASCADE)
    city = models.CharField('Город', max_length=50)
    street = models.CharField('Улица', max_length=100)
    house = models.CharField('Дом', max_length=15, blank=True)
    structure = models.CharField('Корпус', max_length=15, blank=True)
    building = models.CharField('Строение', max_length=15, blank=True)
    apartment = models.CharField('Квартира', max_length=15, blank=True)
    phone = models.CharField('Телефон', max_length=20)

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return f'{self.city}, {self.street}, {self.house}'


class Order(models.Model):
    #Модель заказа

    STATE_CHOICES = (
        ('basket', 'Корзина'),
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('assembled', 'Собран'),
        ('sent', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    )

    user = models.ForeignKey(User, verbose_name='Пользователь',
                             related_name='orders', on_delete=models.CASCADE)
    dt = models.DateTimeField('Дата создания', auto_now_add=True)
    state = models.CharField('Статус', choices=STATE_CHOICES, max_length=15)
    contact = models.ForeignKey(Contact, verbose_name='Контакт',
                                null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('-dt',)

    def __str__(self):
        return f'Заказ #{self.id} от {self.dt.strftime("%d.%m.%Y")}'

    @property
    def total_amount(self):
        return sum(item.quantity * item.product_info.price for item in self.ordered_items.all())


class OrderItem(models.Model):
    #Модель позиции в заказе

    order = models.ForeignKey(Order, verbose_name='Заказ',
                              related_name='ordered_items', on_delete=models.CASCADE)
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте',
                                     related_name='ordered_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('Количество', default=1)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'product_info'],
                name='unique_order_item'
            ),
        ]

    def __str__(self):
        return f'{self.product_info} x {self.quantity}'

    @property
    def total_price(self):
        #Общая стоимость позиции
        return self.quantity * self.product_info.price


class ConfirmEmailToken(models.Model):
    #Модель токена подтверждения email

    user = models.ForeignKey(User, related_name='confirm_email_tokens',
                             on_delete=models.CASCADE, verbose_name="Пользователь")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    key = models.CharField("Ключ", max_length=64, db_index=True, unique=True)

    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        #Генерация уникального ключа
        return get_token_generator().generate_token()

    def __str__(self):
        return f'Токен для {self.user.email}'