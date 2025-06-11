#C:\Users\ASUS Vivobook\PycharmProjects\PythonProject\daju-beri\backend\deals\serializers.py

from django.urls import reverse
from django.utils import timezone
from rest_framework import serializers
from decimal import Decimal

from .models import Deal, Marketplace


class MarketplaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marketplace
        fields = ['id', 'name', 'last_sync']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['name'] = instance.get_name_display()
        return data


class DealSerializer(serializers.ModelSerializer):
    # Вычисляемые поля
    time_remaining = serializers.SerializerMethodField()
    is_expiring_soon = serializers.SerializerMethodField()
    is_new = serializers.SerializerMethodField()
    image_thumbnail = serializers.SerializerMethodField()
    detail_url = serializers.SerializerMethodField()

    # Связные объекты
    marketplace_info = MarketplaceSerializer(source='marketplace', read_only=True)

    class Meta:
        model = Deal
        fields = [
            'id',
            'title',
            'description',
            'original_price',
            'discount_price',
            'discount_percentage',
            'image_url',
            'image_thumbnail',
            'deal_url',
            'category',
            'valid_until',
            'created_at',
            'time_remaining',
            'is_expiring_soon',
            'is_new',
            'marketplace_info',
            'detail_url'
        ]
        read_only_fields = ['created_at', 'discount_percentage']
        extra_kwargs = {
            'marketplace': {'write_only': True},
            'external_id': {'write_only': True},
        }

    # Реализация методов для вычисляемых полей
    def get_time_remaining(self, obj):
        """Рассчитывает оставшееся время действия акции"""
        if obj.valid_until:
            remaining = obj.valid_until - timezone.now()
            return {
                'days': remaining.days,
                'hours': remaining.seconds // 3600,
                'minutes': (remaining.seconds % 3600) // 60
            }
        return None

    def get_is_expiring_soon(self, obj):
        """Проверяет, заканчивается ли акция в ближайшие 24 часа"""
        if obj.valid_until:
            now = timezone.now()
            return now <= obj.valid_until <= (now + timezone.timedelta(hours=24))
        return False

    def get_is_new(self, obj):
        """Проверяет, добавлена ли акция в последние 24 часа"""
        return obj.created_at >= (timezone.now() - timezone.timedelta(hours=24))

    def get_image_thumbnail(self, obj):
        if obj.image_url:
            return obj.image_url.replace('.jpg', '_thumb.jpg')
        return None

    def get_detail_url(self, obj):
        return reverse('deal-detail', kwargs={'pk': obj.id})

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # Форматирование цен для отображения
        data['original_price'] = f"{Decimal(data['original_price']):.2f} ₽"
        data['discount_price'] = f"{Decimal(data['discount_price']):.2f} ₽"

        # Сокращенное описание (добавляем только если нужно в API)
        # Если требуется - добавить 'short_description' в fields
        desc = data.get('description', '')
        if desc:
            data['description'] = (desc[:150] + '...') if len(desc) > 150 else desc

        return data

    def validate(self, data):
        # Валидация только для записей с изменяемыми ценами
        if 'discount_price' in data and 'original_price' in data:
            if data['discount_price'] >= data['original_price']:
                raise serializers.ValidationError(
                    "Цена со скидкой должна быть ниже оригинальной"
                )
        return data