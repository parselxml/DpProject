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

## 👤 Пользователи и авторизация
- Регистрация по email
- Авторизация через JWT/Token
- Подтверждение email через письмо
- Восстановление пароля

## 📦 Основной функционал

### 🔹 Магазины и товары
- `Shop` – магазины
- `Category` – категории товаров
- `Product` – товары
- `ProductInfo` – характеристики и цена товара
- `Parameter` и `ProductParameter` – параметры товара

### 🔹 Заказы и корзина
- Корзина
- Добавление/удаление товаров
- Подсчет итоговой суммы
- Подтверждение заказа и смена статуса

### 🔹 Контакты
- Добавление адресов и телефонов пользователя

### 🔹 Импорт товаров
Пример:
```bash
python manage.py loaddata data/shop1.yaml
```
