# -*- coding: utf-8 -*-

import json
import os
from datetime import timedelta
from os.path import join

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
print
with open(join(BASE_DIR, 'config/settings.json')) as f:
    env = json.load(f)

SECRET_KEY = env['SECRET_KEY']

DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # external apps
    'django_rq',
    # 'debug_toolbar',
    # local apps
    'uptime',
    'api',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env['DB'],
        'USER': env['DB_USER'],
        'PASSWORD': env['DB_PASSWORD'],
        'HOST': 'localhost'
    }
}

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

# Email

EMAIL_HOST = env['EMAIL_HOST']
EMAIL_HOST_USER = env['EMAIL_USER']
EMAIL_HOST_PASSWORD = env['EMAIL_PASSWORD']
DEFAULT_FROM_EMAIL = env['DEFAULT_FROM_EMAIL']
SERVER_EMAIL = env['SERVER_EMAIL']
EMAIL_PORT = 587
EMAIL_USE_TLS = True

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

LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

LOGIN_URL = '/ingresar/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '[%(levelname)s] %(name)s: %(message)s'
        },
        "rq_console": {
            "format": "%(asctime)s %(message)s",
            "datefmt": "%H:%M:%S",
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': "logging.StreamHandler",
            'formatter': 'standard'
        },
        "rq_console": {
            "level": "DEBUG",
            "class": "rq.utils.ColorizingStreamHandler",
            "formatter": "rq_console",
            "exclude": ["%(asctime)s"],
        },
        'uptime': {
            "level": "DEBUG",
            "class": "utils.log.ColorizingStreamHandler",
            "formatter": "standard"
        }
    },
    'loggers': {
        'rq.worker': {
            'handlers': ['rq_console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'uptime': {
            'handlers': ['uptime'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}

# django-rq
RQ_QUEUES = {
    'default': {
        'HOST': env["REDIS_HOST"],
        'PORT': env["REDIS_PORT"],
        'DB': env["REDIS_DB"],
        'PASSWORD': env["REDIS_PASSWORD"],
    }
}

REDIS_CONF = {
    'host': env["REDIS_HOST"],
    'port': env["REDIS_PORT"],
    'db': env["REDIS_DB"],
    'password': env["REDIS_PASSWORD"]
}

###################
# uptime settings #
###################

UPTIME_TIEMPO_ENTRE_CHECKS = 60 * 2  # número de segundos

# tiempo para minimo transcurrido para crear un nuevo evento con el mismo estado
UPTIME_TIEMPO_MINIMO_ENTRE_EVENTOS = timedelta(hours=1)

# tiempo maximo para considerar al ultimo evento como válido.
UPTIME_TIEMPO_MAXIMO_ULTIMO_EVENTO = timedelta(hours=1)

UPTIME_DEFAULT_ELAPSED_TIME = -500

UPTIME_ADMIN_EMAIL = env['ADMIN_EMAIL']

UPTIME_REDIS_PREFIX = 'uptime'

UPTIME_ERRORES_CONSECUTIVOS_PARA_NOTIFICAR = 2

# Tiempo de expiración de los contadores
UPTIME_REDIS_EXPIRE = 60 * 60 * 24
