import os
from pathlib import Path
from datetime import timedelta, datetime

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET")
DEBUG = True
HOST = os.getenv("HOST", "lis.itmo.ru")

ALLOWED_HOSTS = [
    HOST,
    "localhost",
    "127.0.0.1",
    "lis.itmo.ru",
    "dev.lis.itmo.ru",
    "158.160.42.32",
    "51.250.78.144",
    "158.160.63.230",
]

# Application definition
INSTALLED_APPS = [
    # custom admin panel
    "jazzmin",

    # django's basic apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_filters",

    # 3rd-party apps
    "corsheaders",
    "rest_framework",
    "djoser",
    "constance",
    "drf_yasg",
    "import_export",
    "loginas",

    # custom apps
    "accounts",
    "sso_app",
    "lessons",
    "resources",
    "editors",
    "student_tasks",
    "assignments_app"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware"
]

ROOT_URLCONF = "django_core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "django_core.wsgi.application"

# Database
DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "maindb",
        "USER": "maindb",
        "PASSWORD": "maindb",
        "HOST": "lis_db",
        "PORT": "5432",
        "TEST": {
            "NAME": "c_test_3",
        },
    }
}

# SMTP configurations
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "").split(",")
EMAIL_TECH = os.getenv("EMAIL_TECH", "").split(",")

# Celery configurations
CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"
CELERY_TIMEZONE = "Europe/Moscow"

# Django caches configurations
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "lis_back",
        "DB": 1
    }
}

# Constance configurations
CONSTANCE_REDIS_CONNECTION = {
    "host": "redis",
    "port": 6379,
    "db": 2,
}

# Authorizations configs
AUTH_USER_MODEL = "accounts.User"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# CORS headers
# https://pypi.org/project/django-cors-headers/
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:1337",
    "http://127.0.0.1:1337",
]

#CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',  # for localhost (REACT Default)
    'http://localhost:8080',  # for localhost (Developlem
    'https://dev.lis.itmo.ru',
    'http://127.0.0.1:3000',
    'http://localhost:5000',
    'http://localhost:1337'
]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT"
]

# Internationalization
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_L10N = True
USE_TZ = True
CONN_MAX_AGE = None

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/django_static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Jazzmin configuration
JAZZMIN_SETTINGS = {
    "topmenu_links": [
        {"name": "Редактор курсов", "url": "/editor/"},
    ]
}

# ISO SSO
ISU_MANAGER_CONFIG = {
    "client_id": os.getenv("ISU_CLIENT_ID"),
    "response_type": "code",
    "base_uri": "https://id.itmo.ru/auth/realms/itmo/protocol/openid-connect/",
    "redirect_uri": f'https://{HOST}/auth/',
    "scope": os.getenv("ISU_SCOPE"),
    "grant_type": "authorization_code",
    "client_secret": os.getenv("ISU_CLIENT_SECRET"),
    "logout_url": "https://id.itmo.ru/auth/realms/itmo/protocol/openid-connect/logout",
    "post_logout_redirect_uri": f"https://{HOST}/",
}

ENVIRONMENT = os.getenv("ENV", "DEV")

if ENVIRONMENT == "PROD":
    from django_core.configs.prod import *
else:
    from django_core.configs.dev import *

# Auth configurations
DJOSER = {
    "LOGIN_FIELD": "username",
    "TOKEN_MODEL": None,  # We use only JWT
    "HIDE_USERS": True,
}

# Rest Framework configurations

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication"
    ),
    "EXCEPTION_HANDLER": "helpers.exceptions.custom_exception_handler"
}

SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("JWT",),
    "ACCESS_TOKEN_LIFETIME": timedelta(days=365),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=365),
    "ROTATE_REFRESH_TOKENS": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
}

if DEBUG:
    SIMPLE_JWT.update(
        {
            "ACCESS_TOKEN_LIFETIME": timedelta(days=365),
            "REFRESH_TOKEN_LIFETIME": timedelta(days=366),
        }
    )

# LIS Configurations
ULTIMATE_COST = 2500
ULTIMATE_DURATION = 3 * 60 * 60  # секунды
START_COURSE_DATE = datetime(day=1, month=9, year=2022)
CHANGE_SCIENTIFIC_DIRECTOR_ENERGY_COST = 6
DEFAULT_SCIENTIFIC_DIRECTOR_UID = "C4"  # Если не задан, то "" (пустая строка)

LOGGING_ROOT = Path(BASE_DIR, "logs")
LOGGING_ROOT.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "debug": {
            "format": "{levelname} | {asctime}: {module} - {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "debug"
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "debug",
            "filename": str(Path(LOGGING_ROOT, "lis_back.log")),
            "when": "midnight",
            "backupCount": 14,
            "interval": 1
        },
        "celery": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "debug",
            "filename": str(Path(LOGGING_ROOT, "celery.log")),
            "when": "midnight",
            "backupCount": 14,
            "interval": 1
        },
    },
    "loggers": {
        "django": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": True,
        },
        "django.request": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": True,
        },
        "django_core": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": True,
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": True,
        },
        "celery": {
            "level": "INFO",
            "handlers": ["console", "celery"],
            "propagate": True,
        },
    }
}

# Google Integration
GOOGLE_CREDENTIALS = Path(BASE_DIR, "gdrive_creds.json")
GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID", "")

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        },
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    }
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
LOGINAS_REDIRECT_URL = '/api/swagger'
