"""
Django settings for socialDistribution project.

Generated by 'django-admin startproject' using Django 4.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import sys
import os
import django_on_heroku  # top of the file
import dotenv

dotenv.load_dotenv(".env")

DATABASE=os.getenv('DATABASE')
DB_USER=os.getenv('DB_USER')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_HOST=os.getenv('DB_HOST')
if not DATABASE or not DB_USER or not DB_PASSWORD or not DB_HOST:
    raise ValueError('Database creds are missing in environment.')

DOMAIN = os.getenv('DOMAIN')
SCHEME = os.getenv('SCHEME')


if not DOMAIN:
    import socket
    DOMAIN = socket.gethostbyname(socket.gethostname())

if not SCHEME:
    SCHEME = 'http://'

HOST = SCHEME + DOMAIN


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-&bydo(ekh0rml7q&$nja39m&9s@z--ec7cewky8aldy*d=eq90'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
"https://www.distribution.social",
"https://peer2pressure.herokuapp.com",
"https://yoshi-connect.herokuapp.com",
"http://localhost:8000",
"http://127.0.0.1:8000",
"http://0.0.0.0:8000",
"https://p2psd.herokuapp.com",
"http://www.distribution.social",
"http://nicksnfk.dynns.com",
"http://localhost:3000",
"https://d21fo9y212zzon.cloudfront.net"
]

CSRF_TRUSTED_ORIGINS = ["https://d21fo9y212zzon.cloudfront.net"]


# Cross Site Request Forgery
CSRF_USE_SESSIONS = True

CSRF_COOKIE_HTTPONLY = True

# CSRF_COOKIE_SAMESITE = 'Secure'

CSRF_COOKIE_SECURE = True

Session Cookies
SESSION_COOKIE_SAME = 'Secure'

SESSION_COOKIE_SECURE = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

HTTP Strict Transport Security
SECURE_HSTS_PRELOAD = True

SECURE_HSTS_SECONDS = 3600

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'generic_relations',
    'rest_framework_swagger',
    'drf_yasg'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'socialDistribution.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.context_processors.current_author',
            ],
            'builtins': [
                'app.templatetags.extra_tags'
            ]
        },
    },
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

WSGI_APPLICATION = 'socialDistribution.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DATABASE,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': '5432',
    }
}

if 'test' in sys.argv:
    DATABASES['default'] = {
       'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'testdatabase'
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

TIME_ZONE = 'America/Edmonton'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [

    ]
}

#remove it once we make it https
SECURE_SSL_REDIRECT = True
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

django_on_heroku.settings(locals())  # bottom of the file

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# SESSION_COOKIE_SECURE = False
# CSRF_COOKIE_SECURE = False
# SECURE_SSL_REDIRECT = False

