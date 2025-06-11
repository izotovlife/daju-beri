#C:\Users\ASUS Vivobook\PycharmProjects\PythonProject\daju-beri\backend\backend\urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from deals import views

router = routers.DefaultRouter()
router.register(r'deals', views.DealViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]

