#daju-beri\backend\deals\tasks.py

from celery import shared_task
from .api_clients import update_all_deals
from .models import Deal
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def update_deals_task():
    try:
        update_all_deals()
        logger.info(f"Successfully updated deals at {timezone.now()}")
    except Exception as e:
        logger.error(f"Deal update failed: {str(e)}")
        raise


@shared_task
def deactivate_expired_deals():
    expired_count = Deal.objects.filter(
        valid_until__lt=timezone.now(),
        is_active=True
    ).update(is_active=False)

    logger.info(f"Deactivated {expired_count} expired deals")