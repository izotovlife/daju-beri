#C:\Users\ASUS Vivobook\PycharmProjects\PythonProject\daju-beri\backend\deals\utils.py

from django.conf import settings

def generate_affiliate_link(marketplace, product_url):
    partner_id = getattr(settings, f'{marketplace.name.upper()}_PARTNER_ID', None)
    if partner_id:
        return f"{product_url}?partner={partner_id}"
    return product_url


def generate_affiliate_link(deal):
    base_url = deal.deal_url
    partner_id = deal.marketplace.partner_id

    if not partner_id:
        return base_url

    # Параметры для разных платформ
    params = {
        'WB': '?partner={partner_id}',  # Wildberries
        'OZ': '?partner={partner_id}',  # Ozon
        'YM': '?clid={partner_id}',     # Яндекс.Маркет
        'AL': '?affiliate={partner_id}', # AliExpress Russia
        'SB': '?partner={partner_id}',  # СберМегаМаркет
        'CD': '?affiliate={partner_id}', # CDEK Маркет
        'GT': '?partner={partner_id}',  # Getmagnet
        'GO': '?partner={partner_id}'   # Goods
    }

    param_template = params.get(deal.marketplace.name, '')  # Шаблон для конкретной платформы
    if param_template:
        return param_template.format(partner_id=partner_id)
    return base_url