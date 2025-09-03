# signals.py
from typing import Type
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created

from .models import ConfirmEmailToken, User


user_registered = Signal()  # Сигнал о регистрации нового пользователя
order_created = Signal()  # Сигнал о создании нового заказа


@receiver(reset_password_token_created)
def handle_password_reset_token(sender, instance, reset_password_token, **kwargs):
    """
    Обработчик для отправки email с токеном сброса пароля
    """
    email_subject = f"Запрос на сброс пароля для {reset_password_token.user}"
    email_body = f"Ваш токен для сброса пароля: {reset_password_token.key}"

    email_message = EmailMultiAlternatives(
        subject=email_subject,
        body=email_body,
        from_email=settings.EMAIL_HOST_USER,
        to=[reset_password_token.user.email]
    )
    email_message.send()


@receiver(post_save, sender=User)
def handle_new_user_registration(sender: Type[User], instance: User, created: bool, **kwargs):
    """
    Обработчик для отправки email подтверждения при регистрации нового пользователя
    """
    if created and not instance.is_active:
        token, _ = ConfirmEmailToken.objects.get_or_create(user_id=instance.pk)

        email_subject = f"Подтверждение email для {instance.email}"
        email_body = f"Ваш токен подтверждения: {token.key}"

        email_message = EmailMultiAlternatives(
            subject=email_subject,
            body=email_body,
            from_email=settings.EMAIL_HOST_USER,
            to=[instance.email]
        )
        email_message.send()


@receiver(order_created)
def handle_new_order(user_id, **kwargs):
    """
    Обработчик для отправки уведомления о новом заказе
    """
    user = User.objects.get(id=user_id)

    email_subject = "Ваш заказ успешно оформлен"
    email_body = "Благодарим за заказ! Мы начали его обработку."

    email_message = EmailMultiAlternatives(
        subject=email_subject,
        body=email_body,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email]
    )
    email_message.send()