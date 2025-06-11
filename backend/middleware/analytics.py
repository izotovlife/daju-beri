#C:\Users\ASUS Vivobook\PycharmProjects\PythonProject\daju-beri\backend\backend\middleware\analytics.py

import time
from django.db import connection
from .models import APILog


class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time
        queries = len(connection.queries)

        if request.path.startswith('/api/'):
            APILog.objects.create(
                path=request.path,
                method=request.method,
                status_code=response.status_code,
                duration=duration,
                queries=queries,
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

        return response