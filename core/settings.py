"""

pip install Pillow
django-admin startproject educa
django-admin startapp courses
######## dumpdata ########
python manage.py dumpdata courses --indent=2  # вывод в консоль данных
python manage.py dumpdata --help

mkdir courses/fixtures
python manage.py dumpdata courses --indent=2 --output=courses/fixtures/subjects.json
python manage.py loaddata subjects.json  # требует UTF-8, Django ищет файлы в каталоге fixtures/, можно изменить
######## END dumpdata ########


Перетаскивание модулей и курсов
pip install django-braces

Добавление регистрации студентов
python manage.py startapp students

приложение Django, которое позволяет вставлять видео в шаблоны из таких источников, как YouTube и Vimeo, просто предоставляя их общедоступный URL-адрес
pip install django-embed-video

##### Использование кеш-фреймворка #####
# Установка образа Memcached платформы Docker
docker pull memcached
docker run -it --rm --name memcached -p 11211:11211 memcached -m 64
# Установка привязки Python к Memcached
pip install pymemcache==3.5.2

# Django Debug Toolbar
pip install django-debug-toolbar

# Использование сайтового кеша
pip install redis
docker run -it --rm --name redis -p 6379:6379 redis

Отслеживание сервера Redis с помощью приложения Django Redisboard
pip install django-redisboard
pip install attrs  # Нужно для django-redisboard
python manage.py migrate redisboard
http://127.0.0.1:8000/admin/redisboard/redisserver/add/   # Управление Django Redisboard

Вводим Redis  и ссылка  redis://localhost:6379/0

# Django REST framework
pip install djangorestframework
curl http://127.0.0.1:8000/api/subjects/ | json_pp

Потребление RESTful API
pip install requests


"""
import os
from pathlib import Path
# перенаправлять студентов на этот URL-адрес при входе на платформу
from django.urls import reverse_lazy

LOGIN_REDIRECT_URL = reverse_lazy('student_course_list')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-9x5w66xkqa)c6!owg4a*1l)ct-m7sjc7jb%fx&ezlt&&%$-915'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'courses.apps.CoursesConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'students.apps.StudentsConfig',
    'embed_video',  # pip install django-embed-video
    'debug_toolbar',  # Django Debug Toolbar
    'redisboard',  # Отслеживание сервера Redis с помощью приложения Django Redisboard
    'rest_framework',  # Django REST framework
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',  # Django Debug Toolbar
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.cache.UpdateCacheMiddleware', # Использование сайтового кеша
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware', # Использование сайтового кеша
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins': ['courses.templatetags.course'],  # от строго
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

# Папки из которых доставать статические фалы, автоматически берет из Приложение/Статик
# STATICFILES_DIRS = (
#     BASE_DIR / "courses/static",
#     BASE_DIR / "Еще какая то папка ",
# )
# находится место назначения, куда копируются статические файлы и откуда они обслуживаются при развертывании приложения Django.
STATIC_ROOT = BASE_DIR / "staticfolder"

STATIC_URL = 'urlstatic/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Раздача медиафайлов
MEDIA_URL = 'media/'  # базовый URL-адрес, используемый для раздачи медиафайлов
MEDIA_ROOT = BASE_DIR / 'media'  # локальный путь, по которому они находятся

''' Меню отладочных инструментов Django будет отображаться только в том
случае, если ваш IP-адрес соответствует записи в настроечном параметре
INTERNAL_IPS.  '''
INTERNAL_IPS = [
    '127.0.0.1',
]

# Использование сайтового кеша
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 60 * 15  # 15 минут
CACHE_MIDDLEWARE_KEY_PREFIX = 'educa'

# кеш-сервер Memcached
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
#         'LOCATION': '127.0.0.1:11211',
#     }
# }

# Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379',
    }
}

# Django REST framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}
