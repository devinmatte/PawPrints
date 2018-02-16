"""
Django settings for pawprints project.

Generated by 'django-admin startproject' using Django 1.10.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from pawprints import secrets
import raven

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
SAML_FOLDER = os.path.join(BASE_DIR, 'saml')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secrets.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
if 'TRAVIS' in os.environ:
    DEBUG = True

ALLOWED_HOSTS = ["*"]

# Sentry Settings
RAVEN_CONFIG = {
    'dsn': secrets.RAVEN_DSN,
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
}

# Application definition

INSTALLED_APPS = [
    'raven.contrib.django.raven_compat',
    'profile.apps.ProfileConfig',
    'petitions.apps.PetitionsConfig',
    'send_mail.apps.SendMailConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'channels',
    'huey.contrib.djhuey',
]

# Settings for Huey task queue https://huey.readthedocs.io/en/latest/contrib.html#django
HUEY = {
    'name': 'RedisHueyInstance',  # Use db name for huey.
    'result_store': False,  # Do not store return values of tasks.
    'events': True,  # Consumer emits events allowing real-time monitoring.
    'store_none': False,  # If a task returns None, do not save to results.
    'always_eager': DEBUG,  # If DEBUG=True, run synchronously.
    'store_errors': True,  # Store error info if task throws exception.
    'blocking': False,  # Poll the queue rather than do blocking pop.
    'backend_class': 'huey.RedisHuey',  # Use path to redis huey by default,
    'connection': {
        'connection_pool': None,  # Definitely you should use pooling!
        # ... tons of other options, see redis-py for details.

        'url': os.environ.get('REDIS_URL', 'redis://localhost:6379'),  # Allow Redis config via a DSN.
    },
    'consumer': {
        'workers': 2,
        'worker_type': 'thread',
        'initial_delay': 0.1,  # Smallest polling interval, same as -d.
        'utc': True,  # Treat ETAs and schedules as UTC datetimes.
        'periodic': False,
        'scheduler_interval': 1,  # Check schedule every second, -s.
        'check_worker_health': True,  # Enable worker health checks.
        'health_check_interval': 1,  # Check worker health every second.
    },
}

AUTHENTICATION_BACKENDS = ['auth.auth_backend.SAMLSPBackend']

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379')],
            "channel_capacity": {
                "http.request": 10000,
                "websocket.send*": 10000,
            },
        },
        "ROUTING": "pawprints.routing.channel_routing",
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'log.ip_log_middleware.IPLogMiddleware',
]

ROOT_URLCONF = 'pawprints.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'pawprints/templates')],
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

STATICFILES_DIRS = [STATIC_DIR, ]
WSGI_APPLICATION = 'pawprints.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': secrets.DB_NAME,
        'USER': secrets.DB_USER,
        'PASSWORD': secrets.DB_PASSWORD,
        'HOST': secrets.DB_HOST,
        'PORT': secrets.DB_PORT,
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

# Email settings

EMAIL_HOST = secrets.EMAIL_HOST
EMAIL_HOST_USER = secrets.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = secrets.EMAIL_HOST_PASSWORD
EMAIL_PORT = secrets.EMAIL_PORT
EMAIL_USE_TLS = secrets.EMAIL_USE_TLS

STATIC_URL = '/static/'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/profile/'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(name)s : %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'formatter': 'verbose',
        },
        'rotate_file_errors':{
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'log/error.log'),
            'formatter': 'verbose',
            'maxBytes': 90000000,
            'backupCount': 10,
            'encoding': 'utf8'
        },
        'rotate_file_info':{
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'log/info.log'),
            'formatter': 'verbose',
            'maxBytes': 90000000,
            'backupCount': 10,
            'encoding': 'utf8'
        },
    },
    'loggers': {
        'pawprints': {
            'handlers': ['rotate_file_errors', 'sentry'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['rotate_file_errors', 'sentry'],
            'level': 'ERROR',
            'propagate': True,
        },
        'IPRequest': {
            'handlers': ['rotate_file_info'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}


# Secure configs
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
