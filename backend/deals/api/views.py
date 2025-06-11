#backend/deals/api/views.py

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q, F, ExpressionWrapper, DurationField
from django.db.models.functions import Now

from .models import Deal
from .serializers import DealSerializer


class StandardResultsPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    # Для оптимизации больших таблиц
    django_paginator_class = Paginator  # Импортируйте из django.core.paginator


class DealViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DealSerializer
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'marketplace': ['exact'],
        'category': ['exact', 'icontains'],  # Добавляем поиск по частичному совпадению
        'discount_percentage': ['gte', 'lte'],  # Фильтр по диапазону скидок
    }
    search_fields = ['title', 'description']
    ordering_fields = [
        'discount_percentage',
        'created_at',
        'valid_until',
        'time_remaining',  # Новое вычисляемое поле
        'discount_price'  # Добавляем сортировку по цене
    ]
    ordering = ['-discount_percentage']  # Сортировка по умолчанию

    def get_queryset(self):
        """
        Возвращает активные акции с дополнительными оптимизациями:
        - Аннотация времени до окончания акции
        - Оптимизированные фильтры
        - Защита от некорректных параметров
        """
        # Базовый запрос с оптимизацией
        queryset = Deal.objects.filter(is_active=True).select_related('marketplace')

        # 1. Аннотация времени до окончания акции
        queryset = queryset.annotate(
            time_remaining=ExpressionWrapper(
                F('valid_until') - Now(),
                output_field=DurationField()
            )
        )

        # 2. Фильтр по минимальной скидке (с защитой)
        min_discount = self.request.query_params.get('min_discount')
        if min_discount and min_discount.isdigit():
            queryset = queryset.filter(discount_percentage__gte=int(min_discount))

        # 3. Фильтр по максимальной цене
        max_price = self.request.query_params.get('max_price')
        if max_price and max_price.replace('.', '', 1).isdigit():
            queryset = queryset.filter(discount_price__lte=float(max_price))

        # 4. Фильтр по сроку действия
        expires_soon = self.request.query_params.get('expires_soon')
        if expires_soon and expires_soon.lower() == 'true':
            # Акции, заканчивающиеся в ближайшие 24 часа
            time_threshold = timezone.now() + timezone.timedelta(hours=24)
            queryset = queryset.filter(valid_until__lte=time_threshold)

        # 5. Фильтр по новым акциям (последние 24 часа)
        new_deals = self.request.query_params.get('new')
        if new_deals and new_deals.lower() == 'true':
            time_threshold = timezone.now() - timezone.timedelta(hours=24)
            queryset = queryset.filter(created_at__gte=time_threshold)

        # 6. Поиск по категории как по дереву (если категории в формате "parent/child")
        category_search = self.request.query_params.get('category_tree')
        if category_search:
            queryset = queryset.filter(
                Q(category__icontains=category_search) |
                Q(category__startswith=f"{category_search}/")
            )

        return queryset

    def list(self, request, *args, **kwargs):
        """Добавляем мета-информацию в ответ"""
        response = super().list(request, *args, **kwargs)

        # Добавляем информацию о доступных фильтрах
        response.data['filters'] = {
            'marketplaces': list(Marketplace.objects.filter(is_active=True).values('id', 'name')),
            'categories': Deal.objects.filter(is_active=True)
                          .order_by('category')
                          .values_list('category', flat=True)
                          .distinct()[:50]  # Ограничиваем для производительности
        }

        return response