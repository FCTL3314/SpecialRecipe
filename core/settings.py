import logging
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
    INTERNAL_IPS=list,
    PROTOCOL=str,
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
    EMAIL_SEND_INTERVAL_SECONDS=int,
    EMAIL_EXPIRATION_HOURS=int,
    RECIPES_PAGINATE_BY=int,
    CATEGORIES_PAGINATE_BY=int,
    COMMENTS_PAGINATE_BY=int,
)

# Take environment variables from .env file.
environ.Env.read_env(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

INTERNAL_IPS = env.list('INTERNAL_IPS')

PROTOCOL = env('PROTOCOL')

DOMAIN_NAME = env('DOMAIN_NAME')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'django_cleanup',
    'django_summernote',
    'widget_tweaks',

    'recipe',
    'accounts',
    'api',
]

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
    INSTALLED_APPS.append('debug_toolbar')

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'
if DEBUG:
    STATICFILES_DIRS = (BASE_DIR / 'static',)
else:
    STATIC_ROOT = BASE_DIR / 'static'

# Media files

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Accounts

AUTHENTICATION_BACKENDS = [
    'accounts.auth.UserEmailOrUsernameAuth'
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

EMAIL_SEND_INTERVAL_SECONDS = env('EMAIL_SEND_INTERVAL_SECONDS')
EMAIL_EXPIRATION_HOURS = env('EMAIL_EXPIRATION_HOURS')

# Recipes

RECIPES_PAGINATE_BY = env('RECIPES_PAGINATE_BY')
CATEGORIES_PAGINATE_BY = env('CATEGORIES_PAGINATE_BY')
COMMENTS_PAGINATE_BY = env('COMMENTS_PAGINATE_BY')

# Celery

CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}'

CELERY_TASK_TIME_LIMIT = 30 * 60

# Rest framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ]
}

DJOSER = {
    'EMAIL': {
        'password_reset': 'api.accounts.views.PasswordResetEmail'
    },

    'PASSWORD_RESET_CONFIRM_URL': 'accounts/reset/{uid}/{token}',
    'SERIALIZERS': {
        'user': 'api.accounts.serializers.UserSerializer',
        'current_user': 'api.accounts.serializers.UserSerializer',
    },
}
