import os
from datetime import timedelta
from typing import Dict, Any

from django.core.exceptions import ImproperlyConfigured
from dj_core_utils.auth.jwt import get_jwt_config


class CoreSettings:
    # Main environment variables
    DEBUG = os.getenv('DEBUG', 'True') == 'True'

    allowed_hosts_str = os.getenv('ALLOWED_HOSTS', '')
    ALLOWED_HOSTS = allowed_hosts_str.split(
        ',') if allowed_hosts_str else ['*']

    ENABLE_FASTAPI = os.getenv('ENABLE_FASTAPI', 'False') == 'True'
    FASTAPI_HOST = os.getenv('FASTAPI_HOST', '0.0.0.0')
    FASTAPI_PORT = int(os.getenv('FASTAPI_PORT', '8001'))

    # SECRET_KEY secure
    DJANGO_SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
    if not DJANGO_SECRET_KEY and 'django' in globals():
        raise ImproperlyConfigured(
            'La variable DJANGO_SECRET_KEY debe estar configurada')

    SECRET_KEY = DJANGO_SECRET_KEY or 'dummy-key-for-fastapi-only-mode'

    # Database Configuration
    DATABASES: Dict[str, Dict[str, Any]] = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'monolito_db'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'OPTIONS': {'options': '-c search_path=public'}
        }
    }

    # Installed applications
    INSTALLED_APPS = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'rest_framework',
        'rest_framework_simplejwt',
        'corsheaders',
        'django_prometheus',
    ]

    # Middleware
    MIDDLEWARE = [
        'dj_core_utils.middleware.context.CurrentUserMiddleware',
    ]

    # REST Framework
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework_simplejwt.authentication.JWTAuthentication',
        ),
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAuthenticated',
        )
    }

    # JWT
    SIMPLE_JWT = get_jwt_config(
        signing_key=DJANGO_SECRET_KEY,
        custom_config={
            'ACCESS_TOKEN_LIFETIME': timedelta(minutes=120),
        }
    )

    # Logging
    LOGGING_CONFIG = 'logging.config.dictConfig'
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
