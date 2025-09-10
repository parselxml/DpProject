# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Shop, Category, Product, ProductInfo, Parameter, \
    ProductParameter, Order, OrderItem, Contact, \
    ConfirmEmailToken


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Административная панель для управления пользователями"""

    list_display = ('email', 'first_name', 'last_name', 'company', 'type',
                    'is_active')
    list_filter = ('type', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name', 'company')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {
            'fields': ('first_name', 'last_name', 'company', 'position',
                       'type')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups',
                       'user_permissions'),
        }),
        (_('Important Dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name',
                       'last_name', 'company', 'position', 'type'),
        }),
    )

    ordering = ('email',)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'state', 'url')
    list_filter = ('state',)
    search_fields = ('name', 'user__email')
    raw_id_fields = ('user',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('shops',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('product', 'shop', 'external_id', 'price', 'quantity')
    list_filter = ('shop',)
    search_fields = ('product__name', 'shop__name', 'external_id')
    raw_id_fields = ('product', 'shop')


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ('product_info', 'parameter', 'value')
    list_filter = ('parameter',)
    search_fields = ('product_info__product__name', 'parameter__name')
    raw_id_fields = ('product_info', 'parameter')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'state', 'dt', 'contact')
    list_filter = ('state', 'dt')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user', 'contact')
    date_hierarchy = 'dt'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_info', 'quantity')
    search_fields = ('order__user__email', 'product_info__product__name')
    raw_id_fields = ('order', 'product_info')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'street', 'house', 'phone')
    search_fields = ('user__email', 'city', 'street')
    raw_id_fields = ('user',)


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at')
    search_fields = ('user__email', 'key')
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)
