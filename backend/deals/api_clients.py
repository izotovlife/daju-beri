# backend/deals/api_clients.py
import os
import requests
import logging
from django.utils import timezone
from datetime import timedelta
from .models import Deal, Marketplace
from django.conf import settings

logger = logging.getLogger(__name__)


def generate_affiliate_link(marketplace, product_url):
    """Генерация партнерских ссылок"""
    partner_id = marketplace.partner_id
    if not partner_id:
        return product_url

    if marketplace.name == 'WB':  # Wildberries
        return f"https://www.wildberries.ru?partner={partner_id}&target={product_url}"
    elif marketplace.name == 'OZ':  # Ozon
        return f"https://www.ozon.ru?partner={partner_id}&target={product_url}"
    elif marketplace.name == 'YM':  # Яндекс Маркет
        return f"https://market.yandex.ru?clid={partner_id}&target={product_url}"
    elif marketplace.name == 'AL':  # AliExpress
        return f"https://aliexpress.ru?affiliate={partner_id}&target={product_url}"
    elif marketplace.name == 'SB':  # СберМегаМаркет
        return f"https://sbermarket.ru?partner={partner_id}&target={product_url}"
    elif marketplace.name == 'CD':  # CDEK Маркет
        return f"https://cdek.market?affiliate={partner_id}&target={product_url}"
    elif marketplace.name == 'GT':  # Getmagnet
        return f"https://getmagnet.ru?partner={partner_id}&target={product_url}"
    elif marketplace.name == 'GO':  # Goods
        return f"https://goods.ru?partner={partner_id}&target={product_url}"
    return product_url


def update_wildberries_deals(marketplace):
    """Wildberries API"""
    try:
        api_key = marketplace.api_key or os.getenv('WB_API_KEY')
        if not api_key:
            logger.error("Wildberries API key not configured")
            return

        # Пример реального API (адаптируйте под документацию)
        response = requests.get(
            'https://suppliers-api.wildberries.ru/public/api/v1/promotions',
            headers={'Authorization': api_key},
            params={'status': 'active'}
        )
        response.raise_for_status()

        for promotion in response.json().get('promotions', []):
            for product in promotion.get('products', []):
                # Рассчет скидки
                discount_percent = int(promotion.get('discount', 0))
                original_price = product['price']
                discount_price = round(original_price * (1 - discount_percent / 100), 2)

                # Создание объекта
                Deal.objects.update_or_create(
                    external_id=f"WB-{promotion['id']}-{product['id']}",
                    marketplace=marketplace,
                    defaults={
                        'title': product.get('name', 'Акционный товар'),
                        'original_price': original_price,
                        'discount_price': discount_price,
                        'discount_percentage': discount_percent,
                        'deal_url': generate_affiliate_link(marketplace, product['url']),
                        'category': promotion.get('category', ''),
                        'valid_until': timezone.now() + timedelta(days=promotion.get('days_left', 3)),
                        'is_active': True
                    }
                )
        marketplace.last_sync = timezone.now()
        marketplace.save()
    except Exception as e:
        logger.error(f"Wildberries API error: {str(e)}")


def update_ozon_deals(marketplace):
    """Ozon API"""
    try:
        api_key = marketplace.api_key or os.getenv('OZON_API_KEY')
        if not api_key:
            logger.error("Ozon API key not configured")
            return

        # Пример API Ozon
        response = requests.post(
            'https://api-seller.ozon.ru/v1/actions',
            headers={'Client-Id': os.getenv('OZON_CLIENT_ID'), 'Api-Key': api_key},
            json={'status': 'ACTIVE'}
        )
        response.raise_for_status()

        for action in response.json().get('actions', []):
            discount_percent = action.get('discount', 0)
            for product in action.get('products', []):
                Deal.objects.update_or_create(
                    external_id=f"OZ-{action['id']}-{product['id']}",
                    marketplace=marketplace,
                    defaults={
                        'title': product.get('name', 'Акция Ozon'),
                        'original_price': product['price'],
                        'discount_price': round(product['price'] * (1 - discount_percent / 100), 2),
                        'discount_percentage': discount_percent,
                        'deal_url': generate_affiliate_link(marketplace, product['url']),
                        'category': action.get('category', ''),
                        'valid_until': action['end_date'],
                        'is_active': True
                    }
                )
        marketplace.last_sync = timezone.now()
        marketplace.save()
    except Exception as e:
        logger.error(f"Ozon API error: {str(e)}")


def update_yandex_market_deals(marketplace):
    """Яндекс Маркет API"""
    try:
        oauth_token = marketplace.api_key or os.getenv('YANDEX_MARKET_OAUTH_TOKEN')
        campaign_id = os.getenv('YANDEX_CAMPAIGN_ID')
        if not oauth_token or not campaign_id:
            logger.error("Yandex Market credentials not configured")
            return

        url = f"https://api.partner.market.yandex.ru/campaigns/{campaign_id}/offers/prices"
        headers = {'Authorization': f'OAuth {oauth_token}'}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        for offer in response.json().get('offers', []):
            if 'discount' in offer:
                discount_percent = int(offer['discount']['percent'])
                Deal.objects.update_or_create(
                    external_id=f"YM-{offer['id']}",
                    marketplace=marketplace,
                    defaults={
                        'title': offer.get('name', 'Товар на Яндекс Маркете'),
                        'original_price': offer['price']['value'],
                        'discount_price': offer['discount']['value'],
                        'discount_percentage': discount_percent,
                        'deal_url': generate_affiliate_link(marketplace, offer['url']),
                        'category': offer.get('category', ''),
                        'valid_until': timezone.now() + timedelta(days=7),
                        'is_active': True
                    }
                )
        marketplace.last_sync = timezone.now()
        marketplace.save()
    except Exception as e:
        logger.error(f"Yandex Market API error: {str(e)}")


def update_sbermarket_deals(marketplace):
    """СберМегаМаркет API"""
    try:
        api_key = marketplace.api_key or os.getenv('SBERMARKET_API_KEY')
        if not api_key:
            logger.error("SberMarket API key not configured")
            return

        response = requests.get(
            'https://partner.sbermarket.ru/api/v1/promotions',
            headers={'Authorization': f'Token {api_key}'}
        )
        response.raise_for_status()

        for promotion in response.json().get('results', []):
            discount_percent = promotion.get('discount_percent', 0)
            for product in promotion.get('products', []):
                Deal.objects.update_or_create(
                    external_id=f"SB-{promotion['id']}-{product['id']}",
                    marketplace=marketplace,
                    defaults={
                        'title': product.get('name', 'Акция СберМегаМаркет'),
                        'original_price': product['base_price'],
                        'discount_price': product['price'],
                        'discount_percentage': discount_percent,
                        'deal_url': generate_affiliate_link(marketplace, product['url']),
                        'category': promotion.get('category', ''),
                        'valid_until': promotion['end_date'],
                        'is_active': True
                    }
                )
        marketplace.last_sync = timezone.now()
        marketplace.save()
    except Exception as e:
        logger.error(f"SberMarket API error: {str(e)}")


def update_getmagnet_deals(marketplace):
    """Getmagnet API"""
    try:
        api_key = marketplace.api_key or os.getenv('GETMAGNET_API_KEY')
        if not api_key:
            logger.error("Getmagnet API key not configured")
            return

        response = requests.get(
            'https://api.getmagnet.ru/v1/promotions',
            headers={'Authorization': f'Bearer {api_key}'}
        )
        response.raise_for_status()

        for promo in response.json().get('promotions', []):
            discount_percent = promo.get('discount', {}).get('percent', 0)
            Deal.objects.update_or_create(
                external_id=f"GT-{promo['id']}",
                marketplace=marketplace,
                defaults={
                    'title': promo.get('title', 'Акция Getmagnet'),
                    'original_price': promo['old_price'],
                    'discount_price': promo['price'],
                    'discount_percentage': discount_percent,
                    'deal_url': generate_affiliate_link(marketplace, promo['url']),
                    'category': promo.get('category', ''),
                    'valid_until': promo['end_date'],
                    'is_active': True
                }
            )
        marketplace.last_sync = timezone.now()
        marketplace.save()
    except Exception as e:
        logger.error(f"Getmagnet API error: {str(e)}")


def update_goods_deals(marketplace):
    """Goods.ru API"""
    try:
        api_key = marketplace.api_key or os.getenv('GOODS_API_KEY')
        if not api_key:
            logger.error("Goods API key not configured")
            return

        response = requests.get(
            'https://api.goods.ru/promotions',
            params={'api_key': api_key, 'status': 'active'}
        )
        response.raise_for_status()

        for promo in response.json().get('promotions', []):
            for product in promo.get('products', []):
                Deal.objects.update_or_create(
                    external_id=f"GO-{promo['id']}-{product['id']}",
                    marketplace=marketplace,
                    defaults={
                        'title': product.get('name', 'Акция Goods.ru'),
                        'original_price': product['old_price'],
                        'discount_price': product['price'],
                        'discount_percentage': int((1 - product['price'] / product['old_price']) * 100),
                        'deal_url': generate_affiliate_link(marketplace, product['url']),
                        'category': promo.get('category', ''),
                        'valid_until': promo['end_date'],
                        'is_active': True
                    }
                )
        marketplace.last_sync = timezone.now()
        marketplace.save()
    except Exception as e:
        logger.error(f"Goods API error: {str(e)}")


def update_cdek_market_deals(marketplace):
    """CDEK Маркет API"""
    try:
        api_key = marketplace.api_key or os.getenv('CDEK_API_KEY')
        if not api_key:
            logger.error("CDEK Market API key not configured")
            return

        response = requests.get(
            'https://api.cdek.market/promotions',
            headers={'Authorization': f'Bearer {api_key}'}
        )
        response.raise_for_status()

        for promo in response.json().get('promotions', []):
            discount_percent = promo.get('discount_percent', 0)
            Deal.objects.update_or_create(
                external_id=f"CD-{promo['id']}",
                marketplace=marketplace,
                defaults={
                    'title': promo.get('title', 'Акция CDEK Маркет'),
                    'original_price': promo['old_price'],
                    'discount_price': promo['price'],
                    'discount_percentage': discount_percent,
                    'deal_url': generate_affiliate_link(marketplace, promo['url']),
                    'category': promo.get('category', ''),
                    'valid_until': promo['end_date'],
                    'is_active': True
                }
            )
        marketplace.last_sync = timezone.now()
        marketplace.save()
    except Exception as e:
        logger.error(f"CDEK Market API error: {str(e)}")


# Главная функция для обновления всех акций
def update_all_deals():
    for marketplace in Marketplace.objects.filter(is_active=True):
        if marketplace.name == 'WB':
            update_wildberries_deals(marketplace)
        elif marketplace.name == 'OZ':
            update_ozon_deals(marketplace)
        elif marketplace.name == 'YM':
            update_yandex_market_deals(marketplace)
        elif marketplace.name == 'SB':
            update_sbermarket_deals(marketplace)
        elif marketplace.name == 'GT':
            update_getmagnet_deals(marketplace)
        elif marketplace.name == 'GO':
            update_goods_deals(marketplace)
        elif marketplace.name == 'CD':
            update_cdek_market_deals(marketplace)

    # Деактивация устаревших акций
    Deal.objects.filter(valid_until__lt=timezone.now()).update(is_active=False)