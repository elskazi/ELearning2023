"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings            # Раздача медиафайлов на локальном сервере
from django.conf.urls.static import static  # Раздача медиафайлов на локальном сервере


urlpatterns = [
    path('admin/', admin.site.urls),
]

# Раздача медиафайлов на локальном сервере
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)