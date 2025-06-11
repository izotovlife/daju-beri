#C:\Users\ASUS Vivobook\PycharmProjects\PythonProject\daju-beri\backend\backend\wsgi.py

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()

