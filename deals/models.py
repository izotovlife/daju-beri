#C:\Users\ASUS Vivobook\PycharmProjects\PythonProject\daju-beri\backend\deals\models.py

#C:\Users\ASUS Vivobook\PycharmProjects\PythonProject\daju-beri\backend\deals\models.py

from django.db import models
from django.utils import timezone
from decimal import Decimal, InvalidOperation


class Marketplace(models.Model):
    MARKETPLACE_CHOICES = [
        ('WB', 'Wildberries'),
        ('OZ', 'Ozon'),
        ('YM', 'Яндекс Маркет'),
        ('AL', 'AliExpress Russia'),
        ('SB', 'СберМегаМаркет'),
        ('CD', 'CDEK Маркет'),
        ('GT', 'Getmagnet'),
        ('GO', 'Goods'),
    ]

    name = models.CharField(max_length=2, choices=MARKETPLACE_CHOICES)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    partner_id = models.CharField(max_length=100, blank=True, null=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    sync_frequency = models.IntegerField(default=6)  # Часы между синхронизациями

    def __str__(self):
        return self.get_name_display()


class Deal(models.Model):
    external_id = models.CharField(max_length=100, verbose_name="External ID")
    title = models.CharField(max_length=200, verbose_name="Title")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Original Price",
        default=None,
        null=True,
        blank=True
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Discount Price",
        default=None,
        null=True,
        blank=True
    )
    discount_percentage = models.IntegerField(verbose_name="Discount Percentage", null=True, blank=True)
    image_url = models.URLField(blank=True, null=True, verbose_name="Image URL")
    deal_url = models.URLField(verbose_name="Deal URL")
    marketplace = models.ForeignKey(
        Marketplace,
        on_delete=models.CASCADE,
        verbose_name="Marketplace"
    )
    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Category"
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Valid Until"
    )
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        unique_together = ('external_id', 'marketplace')
        indexes = [
            models.Index(fields=['discount_percentage', 'is_active']),  # Комбинированный индекс
            models.Index(fields=['valid_until']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['-created_at']
        verbose_name = "Deal"
        verbose_name_plural = "Deals"

    def __str__(self):
        return f"{self.title} ({self.marketplace.get_name_display()})"

    def save(self, *args, **kwargs):
        # Безопасный расчёт процента скидки
        if self.discount_percentage is None:
            self.calculate_discount_percentage()

        # Установка срока действия по умолчанию
        if not self.valid_until:
            self.valid_until = timezone.now() + timezone.timedelta(days=7)

        # Обновление статуса активности
        self.update_activity_status()

        super().save(*args, **kwargs)

    def calculate_discount_percentage(self):
        """
        Безопасный расчет процента скидки с проверкой значений.
        """
        if isinstance(self.original_price, Decimal) and isinstance(self.discount_price, Decimal):
            try:
                discount_amount = self.original_price - self.discount_price

                if discount_amount <= 0 or self.original_price <= 0:
                    self.discount_percentage = 0
                else:
                    percentage = (discount_amount / self.original_price) * 100
                    self.discount_percentage = int(percentage)
            except (InvalidOperation, TypeError, ValueError):
                self.discount_percentage = 0
        else:
            self.discount_percentage = 0

    def update_activity_status(self):
        """
        Обновляет статус активности сделки на основе её срока действия.
        """
        now = timezone.now()
        if self.valid_until:
            # Сделка активна, пока срок ещё не истек
            self.is_active = self.valid_until > now
        else:
            # Если срок не указан, сделка считается активной
            self.is_active = True

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name