#\daju-beri\backend\deals\views.py

from rest_framework import viewsets
from .models import Deal
from .serializers import DealSerializer

class DealViewSet(viewsets.ModelViewSet):
    queryset = Deal.objects.filter(is_active=True).order_by('-discount_percentage')
    serializer_class = DealSerializer