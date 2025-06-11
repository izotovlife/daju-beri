from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # Рекомендуется убрать переопределение groups и user_permissions,
    # если не меняешь их поведение.

    favorite_categories = models.ManyToManyField(
        'deals.Category',  # Отложенная ссылка строкой
        blank=True,
        related_name='favorited_by_users'
    )
