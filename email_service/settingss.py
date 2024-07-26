
from datetime import timedelta
import os
from pathlib import Path
from decouple import config, Csv
from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Local/project apps
    'emails_app',
    # Other apps
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'django_celery_results',
    'django_celery_beat',
    # 'django_redis',
    "corsheaders",
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

ROOT_URLCONF = 'email_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'email_service.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            # Set MySQL server timezone to East Africa Time
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'; SET time_zone='+03:00';",
            'charset': 'utf8mb4',
        },
    }
}


# Default SMTP settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Dar_es_Salaam'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),

]
STATIC_ROOT = os.path.join(BASE_DIR, "static_root")


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_NAME = 'NIT EMAIL SERVICE'
SITE_NAME_FULL = 'NIT EMAIL SERVICE'
SITE_NAME_SHORT = 'NES'

# ADMINS = [
#     ('Rodrick Mero', 'rodrick.mero@nit.ac.tz'),
#     ('Jovin Kamala', 'jovinkamalajohn@gmail.com')
# ]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = ['http://127.0.0.1']

# Override defaults DJANGO MESSAGE_TAGS TO MATCH BOOTSTRAP-5 COLOR CLASSES
MESSAGE_TAGS = {
    messages.DEBUG: 'primary',
    messages.ERROR: 'danger',
    messages.WARNING: 'warning',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
}


# Celery settings
# CELERY_broker_url = f'redis://:{config("REDIS_SERVER_PASSWORD")}@{config("REDIS_SERVER_HOST")}:{config("REDIS_SERVER_PORT")}/0'
# result_backend = 'django-db'  # Using Django ORM as result backend
# result_backend = f'redis://:{config("REDIS_SERVER_PASSWORD")}@{config("REDIS_SERVER_HOST")}:{config("REDIS_SERVER_PORT")}/0'
# result_backend = 'django-cache'
# CELERY_broker_connection_retry_on_startup = True


# Celery settings
CELERY_BROKER_URL = f'redis://:{config("REDIS_SERVER_PASSWORD")}@{config("REDIS_SERVER_HOST")}:{config("REDIS_SERVER_PORT")}'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True


# Redis configuration for Django cache and sessions (if needed)
# django setting.
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{config("REDIS_SERVER_HOST")}:{config("REDIS_SERVER_PORT")}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': f'{config("REDIS_SERVER_PASSWORD")}',
        }
    }
}


SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
# "django.contrib.sessions.backends.db": Stores session data in the database (default).
# "django.contrib.sessions.backends.cache": Stores session data in the cache.
# "django.contrib.sessions.backends.cached_db": Stores session data in the cache and database.
# "django.contrib.sessions.backends.file": Stores session data in the file system.
# "django.contrib.sessions.backends.signed_cookies": Stores session data in a cookie,


# Celery beats settings
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
