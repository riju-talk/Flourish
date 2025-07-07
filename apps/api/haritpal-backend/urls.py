from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/', include('core.urls')),
    path('ai-chat/', include('ai.urls')),
]

# wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'haritpal_backend.settings')
application = get_wsgi_application()