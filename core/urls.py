"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings  # Раздача медиафайлов на локальном сервере
from django.conf.urls.static import static  # Раздача медиафайлов на локальном сервере
from django.contrib.auth import views as auth_views  # login logout

urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(),name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(),name='logout'),
    path('admin/', admin.site.urls),
]

# Раздача медиафайлов на локальном сервере
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
