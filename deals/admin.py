#C:\Users\ASUS Vivobook\PycharmProjects\PythonProject\daju-beri\backend\deals\admin.py

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import Marketplace, Deal


@admin.register(Marketplace)
class MarketplaceAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'is_active', 'last_sync', 'sync_frequency', 'status_icon')
    list_editable = ('is_active', 'sync_frequency')
    search_fields = ('name',)
    list_filter = ('is_active',)
    actions = ['activate_marketplaces', 'deactivate_marketplaces']

    def display_name(self, obj):
        """Отображение названия маркетплейса с иконкой"""
        return f"🛒 {obj.get_name_display()}"
    display_name.short_description = 'Marketplace'

    def status_icon(self, obj):
        """Иконка статуса активности"""
        return "✅" if obj.is_active else "❌"
    status_icon.short_description = 'Status'

    @admin.action(description="Activate selected marketplaces")
    def activate_marketplaces(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} marketplaces activated")

    @admin.action(description="Deactivate selected marketplaces")
    def deactivate_marketplaces(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} marketplaces deactivated")


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    search_fields = ('title', 'description', 'category__name')
    list_filter = ('marketplace__name', 'is_active', 'category')
    readonly_fields = ('created_at', 'updated_at', 'time_until_expiry')
    list_per_page = 50
    date_hierarchy = 'valid_until'
    actions = ['activate_deals', 'deactivate_deals', 'mark_as_expired']

    fieldsets = (
        ("Основная информация", {
            'fields': (
                'title',
                'description',
                'marketplace',
                'category',
                'is_active',
            )
        }),
        ("Цены и скидки", {
            'fields': (
                'original_price',
                'discount_price',
                'discount_percentage',
            ),
            'classes': ('collapse',)
        }),
        ("Ссылки и изображения", {
            'fields': ('image_url', 'deal_url'),
            'classes': ('collapse',)
        }),
        ("Срок действия", {
            'fields': (
                'valid_until',
                'time_until_expiry'
            )
        }),
        ("Системная информация", {
            'fields': (
                'external_id',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

    def get_list_editable(self, request):
        """Динамическое управление редактируемыми полями"""
        if request.user.is_superuser:
            return ('is_active',)
        return ()

    def get_list_display(self, request):
        """Динамическое отображение полей"""
        base_fields = (
            'title_with_link',
            'marketplace_display',
            'price_info',
            'discount_percentage',
            'formatted_valid_until',
            'created_ago',
        )
        if request.user.is_superuser:
            return base_fields + ('is_active', 'status_badge', 'updated_at')
        return base_fields + ('status_badge',)

    def title_with_link(self, obj):
        """Название со ссылкой на сделку"""
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            obj.deal_url,
            obj.title
        )
    title_with_link.short_description = 'Title'
    title_with_link.admin_order_field = 'title'

    def marketplace_display(self, obj):
        """Отображение маркетплейса с иконкой"""
        if obj.marketplace:
            return f"🏪 {obj.marketplace.get_name_display()}"
        return "❌ Не указан"
    marketplace_display.short_description = 'Marketplace'

    def price_info(self, obj):
        """Отображение цен и экономии"""
        return format_html(
            "<span style='text-decoration: line-through;'>{}</span> → "
            "<span style='color: red; font-weight: bold;'>{}</span> "
            "<span style='color: green;'>(Save {} руб.)</span>",
            f"{obj.original_price} руб.",
            f"{obj.discount_price} руб.",
            int(obj.original_price - obj.discount_price)
        )
    price_info.short_description = 'Price'

    def status_badge(self, obj):
        """Бейдж статуса"""
        if obj.is_active:
            if obj.valid_until and obj.valid_until < timezone.now():
                return format_html(
                    "<span style='background-color: #ff9800; padding: 3px 6px; border-radius: 4px; color: white;'>EXPIRED</span>"
                )
            return format_html(
                "<span style='background-color: #4caf50; padding: 3px 6px; border-radius: 4px; color: white;'>ACTIVE</span>"
            )
        return format_html(
            "<span style='background-color: #f44336; padding: 3px 6px; border-radius: 4px; color: white;'>INACTIVE</span>"
        )
    status_badge.short_description = 'Status'

    def formatted_valid_until(self, obj):
        """Форматированная дата окончания"""
        if obj.valid_until:
            return obj.valid_until.strftime("%d.%m.%Y %H:%M")
        return "-"
    formatted_valid_until.short_description = 'Valid Until'

    def created_ago(self, obj):
        """Время с момента создания"""
        delta = timezone.now() - obj.created_at
        if delta.days > 0:
            return f"{delta.days} дней назад"
        hours = delta.seconds // 3600
        if hours > 0:
            return f"{hours} часов назад"
        minutes = (delta.seconds // 60) % 60
        return f"{minutes} минут назад"
    created_ago.short_description = 'Создано'

    def time_until_expiry(self, obj):
        """Время до истечения срока"""
        if not obj.valid_until:
            return "Без срока действия"
        if obj.valid_until < timezone.now():
            return "ИСТЕК"

        delta = obj.valid_until - timezone.now()
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds // 60) % 60

        if days > 0:
            return f"{days} дней, {hours} часов"
        if hours > 0:
            return f"{hours} часов, {minutes} минут"
        return f"{minutes} минут"
    time_until_expiry.short_description = 'Осталось времени'

    @admin.action(description="Activate selected deals")
    def activate_deals(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Активировано {updated} сделок")

    @admin.action(description="Deactivate selected deals")
    def deactivate_deals(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Деактивировано {updated} сделок")

    @admin.action(description="Mark as expired")
    def mark_as_expired(self, request, queryset):
        updated = queryset.update(
            is_active=False,
            valid_until=timezone.now() - timezone.timedelta(days=1)
        )
        self.message_user(request, f"Помечено как истекшие: {updated} сделок")

    def get_fieldsets(self, request, obj=None):
        """Динамические поля в зависимости от разрешения"""
        fieldsets = super().get_fieldsets(request, obj)
        if not request.user.is_superuser:
            return [fs for fs in fieldsets if fs[0] != "Системная информация"]
        return fieldsets

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "marketplace":
            # Показываем только активные маркетплейсы
            kwargs["queryset"] = Marketplace.objects.filter(is_active=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
