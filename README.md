# Django Магазин (Diplom Project)

##  Описание проекта
Проект представляет собой **интернет-магазин** с API, реализованным на Django REST Framework.
Функционал позволяет:
- Управлять магазинами и товарами
- Импортировать данные о товарах
- Работать с корзиной и заказами
- Регистрировать пользователей и подтверждать email
- Отслеживать статус заказов через личный кабинет или админ-панель

## Технологический стек
- Python 3.11+
- Django 5.2.5
- Django REST Framework
- SQLite 
- PyYAML
- django-rest-passwordreset (восстановление пароля)

## Структура проекта
```
DjangoProject/
│── manage.py
│── requirements.txt
│── data/shop1.yaml
│
├── Diplom/                 # Конфигурация проекта
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── shop/                   # Основное приложение
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── services.py
    ├── signals.py
    ├── admin.py
    └── tests.py
```

##  Установка и запуск

### 1. Клонирование проекта
```bash
git clone https://github.com/parselxml/DpProject.git
cd DpProject
```

### 2. Создание виртуального окружения
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate    # Windows
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения
Создайте файл `.env` в корне проекта:
```
SECRET_KEY=секретный_ключ
DEBUG=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=ваш_email@gmail.com
EMAIL_HOST_PASSWORD=пароль_или_app_password
DEFAULT_FROM_EMAIL=ваш_email@gmail.com
```

### 5. Миграции базы данных
```bash
python manage.py migrate
```

### 6. Создание суперпользователя
```bash
python manage.py createsuperuser
```

### 7. Запуск сервера
```bash
python manage.py runserver
```


## Модели данных
Основные сущности:
- **User** - Пользователи системы (покупатели и магазины)
- **Shop** - Магазины-партнеры
- **Product** - Товары с категориями
- **Order** - Заказы с различными статусами
- **Contact** - Контактная информация пользователей
- **ProductInfo** - Детальная информация о товарах

## Аутентификация и авторизация
Методы аутентификации:
- Token Authentication
- Session Authentication

Роли пользователей:
- **Покупатель (buyer)** - Просмотр товаров, управление корзиной, оформление заказов
- **Магазин (shop)** - Управление товарами, просмотр заказов


## API Endpoints

### Аутентификация
| Метод |                              Endpoint | Описание                        |
|-------|--------------------------------------:|---------------------------------|
| POST  |               `/api/v1/user/register` | Регистрация нового пользователя |
| POST  |       `/api/v1/user/register/confirm` | Подтверждение email             |
| POST  |                  `/api/v1/user/login` | Авторизация                     |
| POST  |         `/api/v1/user/password_reset` | Запрос сброса пароля            |
| POST  | `/api/v1/user/password_reset/confirm` | Подтверждение сброса пароля     |

### Управление пользователем
| Метод |               Endpoint | Описание                       |
|-------|-----------------------:|--------------------------------|
| GET   | `/api/v1/user/details` | Получение данных пользователя  |
| POST  | `/api/v1/user/details` | Обновление данных пользователя |

### Магазины и товары
| Метод |                Endpoint | Описание                      |
|-------|------------------------:|-------------------------------|
| GET   |         `/api/v1/shops` | Список активных магазинов     |
| GET   |    `/api/v1/categories` | Список категорий              |
| GET   |      `/api/v1/products` | Поиск товаров с фильтрацией   |
| GET   | `/api/v1/products/{id}` | Детальная информация о товаре |

### Корзина
| Метод  |         Endpoint | Описание                      |
|--------|-----------------:|-------------------------------|
| GET    | `/api/v1/basket` | Просмотр корзины              |
| POST   | `/api/v1/basket` | Добавление товаров в корзину  |
| PUT    | `/api/v1/basket` | Обновление количества товаров |
| DELETE | `/api/v1/basket` | Удаление товаров из корзины   |

### Заказы
| Метод |        Endpoint | Описание          |
|-------|----------------:|-------------------|
| GET   | `/api/v1/order` | История заказов   |
| POST  | `/api/v1/order` | Оформление заказа |

### Контакты
| Метод  |               Endpoint | Описание            |
|--------|-----------------------:|---------------------|
| GET    | `/api/v1/user/contact` | Получение контактов |
| POST   | `/api/v1/user/contact` | Добавление контакта |
| PUT    | `/api/v1/user/contact` | Обновление контакта |
| DELETE | `/api/v1/user/contact` | Удаление контактов  |

### Партнерский функционал
| Метод |                 Endpoint | Описание                   |
|-------|-------------------------:|----------------------------|
| POST  | `/api/v1/partner/update` | Импорт прайс-листа         |
| GET   |  `/api/v1/partner/state` | Получение статуса магазина |
| POST  |  `/api/v1/partner/state` | Изменение статуса магазина |
| GET   | `/api/v1/partner/orders` | Заказы магазина            |



# Примеры запросов и ответов

## Аутентификация

### 1. Регистрация пользователя
**POST** `/api/v1/user/register`

**Тело запроса:**
```json
{
  "first_name": "Иван",
  "last_name": "Иванов",
  "email": "ivan@example.com",
  "password": "securepassword123",
  "company": "ООО Ромашка",
  "position": "Менеджер"
}
```

**Успешный ответ:**
```json
{
  "Status": true
}
```

**Ошибка:**
```json
{
  "Status": false,
  "Errors": {
    "password": ["Пароль слишком простой"]
  }
}
```

---

### 2. Подтверждение email
**POST** `/api/v1/user/register/confirm`

**Тело запроса:**
```json
{
  "email": "ivan@example.com",
  "token": "abc123def456"
}
```

**Успешный ответ:**
```json
{
  "Status": true
}
```

**Ошибка:**
```json
{
  "Status": false,
  "Errors": "Неправильно указан токен или email"
}
```

---

### 3. Авторизация
**POST** `/api/v1/user/login`

**Тело запроса:**
```json
{
  "email": "ivan@example.com",
  "password": "securepassword123"
}
```

**Успешный ответ:**
```json
{
  "Status": true,
  "Token": "c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d"
}
```

**Ошибка:**
```json
{
  "Status": false,
  "Errors": "Ошибка авторизации"
}
```

---

### 4. Сброс пароля
**POST** `/api/v1/user/password_reset`

**Тело запроса:**
```json
{
  "email": "ivan@example.com"
}
```

**Успешный ответ:**
```json
{
  "Status": true
}
```

---

## Управление пользователем

### 5. Получение данных пользователя
**GET** `/api/v1/user/details`

**Заголовки:**
```
Authorization: Token c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d
```

**Успешный ответ:**
```json
{
  "id": 1,
  "first_name": "Иван",
  "last_name": "Иванов",
  "email": "ivan@example.com",
  "company": "ООО Ромашка",
  "position": "Менеджер",
  "contacts": [
    {
      "id": 1,
      "city": "Москва",
      "street": "Ленина",
      "house": "10",
      "structure": "",
      "building": "",
      "apartment": "25",
      "phone": "+79161234567"
    }
  ]
}
```

---

### 6. Обновление данных пользователя
**POST** `/api/v1/user/details`

**Заголовки:**
```
Authorization: Token c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d
```

**Тело запроса:**
```json
{
  "first_name": "Иван",
  "last_name": "Петров",
  "company": "ИП Петров",
  "position": "Директор"
}
```

**Успешный ответ:**
```json
{
  "Status": true
}
```

---

## Магазины и категории

### 7. Получение списка магазинов
**GET** `/api/v1/shops`

**Успешный ответ:**
```json
[
  {
    "id": 1,
    "name": "Магазин электроники",
    "state": true
  },
  {
    "id": 2,
    "name": "Книжный магазин",
    "state": true
  }
]
```

---

### 8. Получение списка категорий
**GET** `/api/v1/categories`

**Успешный ответ:**
```json
[
  {
    "id": 1,
    "name": "Электроника"
  },
  {
    "id": 2,
    "name": "Книги"
  }
]
```

---

## Товары

### 9. Поиск товаров
**GET** `/api/v1/products?shop_id=1&category_id=2`

**Успешный ответ:**
```json
[
  {
    "id": 1,
    "model": "XYZ-100",
    "product": {
      "name": "Смартфон",
      "category": "Электроника"
    },
    "shop": 1,
    "quantity": 15,
    "price": 25000,
    "price_rrc": 27000,
    "product_parameters": [
      {
        "parameter": "Цвет",
        "value": "Черный"
      },
      {
        "parameter": "Память",
        "value": "128GB"
      }
    ]
  }
]
```

---

### 10. Получение деталей товара
**GET** `/api/v1/products/1`

**Заголовки:**
```
Authorization: Token c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d
```

**Успешный ответ:**
```json
{
  "id": 1,
  "model": "XYZ-100",
  "product": {
    "name": "Смартфон",
    "category": "Электроника"
  },
  "shop": 1,
  "quantity": 15,
  "price": 25000,
  "price_rrc": 27000,
  "product_parameters": [
    {
      "parameter": "Цвет",
      "value": "Черный"
    }
  ]
}
```

---

## Корзина

### 11. Получение корзины
**GET** `/api/v1/basket`

**Заголовки:**
```
Authorization: Token c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d
```

**Успешный ответ:**
```json
[
  {
    "id": 5,
    "ordered_items": [
      {
        "id": 10,
        "product_info": {
          "id": 1,
          "model": "XYZ-100",
          "product": {
            "name": "Смартфон",
            "category": "Электроника"
          },
          "shop": 1,
          "quantity": 15,
          "price": 25000,
          "price_rrc": 27000,
          "product_parameters": [
            {
              "parameter": "Цвет",
              "value": "Черный"
            }
          ]
        },
        "quantity": 2
      }
    ],
    "state": "basket",
    "dt": "2024-01-15T10:30:00Z",
    "total_sum": 50000,
    "contact": null
  }
]
```

---

### 12. Добавление в корзину
**POST** `/api/v1/basket`

**Заголовки:**
```
Authorization: Token c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d
```

**Тело запроса:**
```json
{
  "items": "[{\"product_info\": 1, \"quantity\": 2}]"
}
```

**Успешный ответ:**
```json
{
  "Status": true,
  "Создано объектов": 1
}
```

---

### 13. Обновление корзины
**PUT** `/api/v1/basket`

**Заголовки:**
```
Authorization: Token c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d
```

**Тело запроса:**
```json
{
  "items": "[{\"id\": 10, \"quantity\": 3}]"
}
```

**Успешный ответ:**
```json
{
  "Status": true,
  "Обновлено объектов": 1
}
```

---

### 14. Удаление из корзины
**DELETE** `/api/v1/basket?items=10,11`

**Заголовки:**
```
Authorization: Token c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d
```

**Успешный ответ:**
```json
{
  "Status": true,
  "Удалено объектов": 2
}
```

---

## Контакты

### 15. Получение контактов
**GET** `/api/v1/user/contact`

**Заголовки:**
```
Authorization: Token c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d
```

**Успешный ответ:**
```json
[
  {
    "id": 1,
    "city": "Москва",
    "street": "Ленина",
    "house": "10",
    "structure": "",
    "building": "",
    "apartment": "25",
    "phone": "+79161234567"
  }
]
```

---

### 16. Добавление контакта
**POST** `/api/v1/user/contact`

**Заголовки:**
```
Authorization: Token c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d
```

**Тело запроса:**
```json
{
  "city": "Санкт-Петербург",
  "street": "Невский проспект",
  "house": "25",
  "apartment": "10",
  "phone": "+79169876543"
}
```

**Успешный ответ:**
```json
{
  "Status": true
}
```

---

### 17. Обновление контакта
**PUT** `/api/v1/user/contact`

**Заголовки:**
```
Authorization: Token c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d
```

**Тело запроса:**
```json
{
  "id": 1,
  "city": "Москва",
  "street": "Тверская",
  "house": "15"
}
```

**Успешный ответ:**
```json
{
  "Status": true
}
```

---

### 18. Удаление контактов
**DELETE** `/api/v1/user/contact`

**Заголовки:**
```
Authorization: Token c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d
```

**Тело запроса:**
```json
{
  "items": "1,2"
}
```

**Успешный ответ:**
```json
{
  "Status": true,
  "Удалено объектов": 2
}
```

---

## Заказы

### 19. Получение истории заказов
**GET** `/api/v1/order`

**Заголовки:**
```
Authorization: Token c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d
```

**Успешный ответ:**
```json
[
  {
    "id": 100,
    "ordered_items": [
      {
        "id": 200,
        "product_info": {
          "id": 1,
          "model": "XYZ-100",
          "product": {
            "name": "Смартфон",
            "category": "Электроника"
          },
          "shop": 1,
          "quantity": 15,
          "price": 25000,
          "price_rrc": 27000,
          "product_parameters": [
            {
              "parameter": "Цвет",
              "value": "Черный"
            }
          ]
        },
        "quantity": 1
      }
    ],
    "state": "new",
    "dt": "2024-01-15T11:30:00Z",
    "total_sum": 25000,
    "contact": {
      "id": 1,
      "city": "Москва",
      "street": "Ленина",
      "house": "10",
      "structure": "",
      "building": "",
      "apartment": "25",
      "phone": "+79161234567"
    }
  }
]
```

---

### 20. Оформление заказа
**POST** `/api/v1/order`

**Заголовки:**
```
Authorization: Token c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d
```

**Тело запроса:**
```json
{
  "id": 5,
  "contact": 1
}
```

**Успешный ответ:**
```json
{
  "Status": true
}
```

---

## Партнерский функционал

### 21. Обновление прайс-листа
**POST** `/api/v1/partner/update`

**Заголовки:**
```
Authorization: Token c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d
```

**Тело запроса:**
```json
{
  "url": "https://example.com/prices.yml"
}
```

**Успешный ответ:**
```json
{
  "Status": true
}
```

---

### 22. Получение статуса магазина
**GET** `/api/v1/partner/state`

**Заголовки:**
```
Authorization: Token c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d
```

**Успешный ответ:**
```json
{
  "id": 1,
  "name": "Магазин электроники",
  "state": true
}
```

---

### 23. Изменение статуса магазина
**POST** `/api/v1/partner/state`

**Заголовки:**
```
Authorization: Token c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d
```

**Тело запроса:**
```json
{
  "state": false
}
```

**Успешный ответ:**
```json
{
  "Status": true
}
```

---

### 24. Получение заказов партнера
**GET** `/api/v1/partner/orders`

**Заголовки:**
```
Authorization: Token c84a6b3d9f2e4a7b8c1d5e6f7a8b9c0d
```

**Успешный ответ:**
```json
[
  {
    "id": 100,
    "ordered_items": [
      {
        "id": 200,
        "product_info": {
          "id": 1,
          "model": "XYZ-100",
          "product": {
            "name": "Смартфон",
            "category": "Электроника"
          },
          "shop": 1,
          "quantity": 15,
          "price": 25000,
          "price_rrc": 27000,
          "product_parameters": [
            {
              "parameter": "Цвет",
              "value": "Черный"
            }
          ]
        },
        "quantity": 1
      }
    ],
    "state": "new",
    "dt": "2024-01-15T11:30:00Z",
    "total_sum": 25000,
    "contact": {
      "id": 1,
      "city": "Москва",
      "street": "Ленина",
      "house": "10",
      "structure": "",
      "building": "",
      "apartment": "25",
      "phone": "+79161234567"
    }
  }
]
```
