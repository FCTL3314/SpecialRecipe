"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from datetime import timedelta
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables

env = environ.Env(
    DEBUG=bool,
    SECRET_KEY=str,
    DOMAIN_NAME=str,
    ALLOWED_HOSTS=list,
    DATABASE_NAME=str,
    DATABASE_USER=str,
    DATABASE_PASSWORD=str,
    DATABASE_HOST=str,
    DATABASE_PORT=str,
    REDIS_HOST=str,
    REDIS_PORT=str,
    EMAIL_HOST=str,
    EMAIL_PORT=str,
    EMAIL_HOST_USER=str,
    EMAIL_HOST_PASSWORD=str,
    EMAIL_USE_SSL=bool,
    RECIPES_PAGINATE_BY=int,
)

# Take environment variables from .env file.
environ.Env.read_env(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

INTERNAL_IPS = [
    '127.0.0.1'
]

DOMAIN_NAME = env('DOMAIN_NAME')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_cleanup',
    'django_summernote',

    'recipe',
    'accounts',
    'api',
]

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'common.context_processors.current_url_name',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': env('DATABASE_NAME'),
            'USER': env('DATABASE_USER'),
            'PASSWORD': env('DATABASE_PASSWORD'),
            'HOST': env('DATABASE_HOST'),
            'PORT': env('DATABASE_PORT'),
        }
    }

# Redis

REDIS_HOST = env('REDIS_HOST')
REDIS_PORT = env('REDIS_PORT')

# Cache

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Logging

FILE_HANDLER = {
    'class': 'logging.handlers.RotatingFileHandler',
    'maxBytes': 1024 * 1024 * 10,
    'backupCount': 10,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'detailed': {
            'format': '[{asctime}] - {levelname} - {filename} on line {lineno}:\n{message}\n\n',
            'datefmt': "%Y/%b/%d %H:%M:%S",
            'style': '{',
        },

        'brief': {
            'format': '[{asctime}] - {levelname}:\n{message}',
            'datefmt': "%Y/%b/%d %H:%M:%S",
            'style': '{',
        },
    },

    'handlers': {
        'file_django': dict(
            FILE_HANDLER,
            formatter='detailed',
            filename=(BASE_DIR / 'logs/django.log'),
        ),

        'file_mailing': dict(
            FILE_HANDLER,
            formatter='brief',
            filename=(BASE_DIR / 'logs/mailing.log'),
            level='INFO',
        ),

        'file_accounts': dict(
            FILE_HANDLER,
            formatter='brief',
            filename=(BASE_DIR / 'logs/accounts.log'),
            level='INFO',
        ),
    },

    'loggers': {
        'django': {
            'handlers': ['file_django'],
            'level': 'WARNING',
        },

        "mailings": {
            "handlers": ["file_mailing"],
            "level": "INFO",
        },

        "accounts": {
            "handlers": ["file_accounts"],
            "level": "INFO",
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'
if DEBUG:
    STATICFILES_DIRS = (BASE_DIR / 'static',)
else:
    STATIC_ROOT = BASE_DIR / 'static'

# Media files

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Accounts

AUTHENTICATION_BACKENDS = [
    'accounts.auth.EmailOrUsernameAuth'
]

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = '/accounts/login/'

LOGOUT_REDIRECT_URL = '/'

# Email

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
else:
    EMAIL_HOST = env('EMAIL_HOST')
    EMAIL_PORT = env('EMAIL_PORT')
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
    EMAIL_USE_SSL = env('EMAIL_USE_SSL')

# Recipes

RECIPES_PAGINATE_BY = env('RECIPES_PAGINATE_BY')

# Celery

CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}'

CELERY_TASK_TIME_LIMIT = 30 * 60

# Rest framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ]
}

DJOSER = {
    'EMAIL': {
        'password_reset': 'api.views.accounts.PasswordResetEmail'
    },

    'PASSWORD_RESET_CONFIRM_URL': 'accounts/reset/{uid}/{token}',
    'SERIALIZERS': {
        'user': 'api.serializers.accounts.UserSerializer',
        'current_user': 'api.serializers.accounts.UserSerializer',
    },
}
