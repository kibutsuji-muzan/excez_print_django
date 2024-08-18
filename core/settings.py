from datetime import timedelta
from pathlib import Path
from rest_framework.settings import api_settings
import os
from django.core.management.utils import get_random_secret_key
import firebase_admin
from firebase_admin import credentials
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-m2v6w@+0j=&8gew)3&nj+d!k^=ob+4ylj1cytvd_a85sm3v63&"

BACKGROUND_TASK_RUN_ASYNC = True
CELERY_BROKER_URL = "redis://127.0.0.1:6379"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379"
CELERY_ACCEPT_CONTENT = {'application/json'}
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'
# SECURITY WARNING: don't run with debug turned on in production!

#CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
#CELERY_ACCEPT_CONTENT = {'application/json'}
#CELERY_RESULT_SERIALIZER = 'json'
#CELERY_TASK_SERIALIZER = 'json'
#CELERY_TIMEZONE = 'Europe/Paris'
#CELERY_RESULT_BACKEND = 'django-db'

DEBUG = True

ALLOWED_HOSTS = [os.environ['DJANGO_ALLOWED_HOST'], "localhost","127.0.0.1"]

# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    "daphne",
    "material",
    "material.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # other packages
    "gdstorage",
    # "django_payments_razorpay",
    "knox",
    "rest_framework",
    "post_office",
    "phonenumber_field",
    "accounts.apps.AccountsConfig",
    "exizprint.apps.ExizprintConfig",
    "django_celery_results",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
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

# WSGI_APPLICATION = "core.wsgi.application"

ASGI_APPLICATION = "core.asgi.application"
CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ['DB_NAME'],
        "USER": os.environ['DB_USER'],
        "PASSWORD":os.environ['DB_PASS'],
        "HOST": "localhost",
        "PORT": "",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("knox.auth.TokenAuthentication",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Calcutta"

USE_TZ = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

MEDIA_URL = "media/"

MEDIA_ROOT = BASE_DIR / "media"

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "static"


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
REST_KNOX = {
    "SECURE_HASH_ALGORITHM": "cryptography.hazmat.primitives.hashes.SHA512",
    "AUTH_TOKEN_CHARACTER_LENGTH": 64,  # By default, it is set to 64 characters (this shouldn't need changing).
    "TOKEN_TTL": timedelta(
        days=(365)
    ),  # The default is 10 hours i.e., timedelta(hours=10)).
    "TOKEN_LIMIT_PER_USER": None,  # By default, this option is disabled and set to None -- thus no limit.
    "AUTO_REFRESH": True,  # This defines if the token expiry time is extended by TOKEN_TTL each time the token is used.
    "EXPIRY_DATETIME_FORMAT": api_settings.DATETIME_FORMAT,
}

###----Emailing Settings----###

#EMAIL_BACKEND = "post_office.EmailBackend"
#EMAIL_HOST = "smtp-mail.outlook.com"
#EMAIL_HOST_USER =os.environ['EMAIL_USER']
#EMAIL_PORT = 587
#EMAIL_HOST_PASSWORD = os.environ['EMAIL_PASS']
#EMAIL_USE_TLS = True

EMAIL_BACKEND = "post_office.EmailBackend"

EMAIL_HOST = "smtp.hostinger.com"
EMAIL_HOST_USER =os.environ['EMAIL_USER']
EMAIL_PORT = 465
EMAIL_HOST_PASSWORD = os.environ['EMAIL_PASS']
EMAIL_USE_SSL = True


cred = credentials.Certificate(
   os.environ['FIREBASE_CERTIFICATE']
)
firebase_admin.initialize_app(cred)

GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE = (
   os.environ['GSTORAGE_CERTIFICATE']
)
GOOGLE_DRIVE_STORAGE_MEDIA_ROOT = "/exizprint/"

p_key = os.environ['RAZORPAY_PUBLIC']
s_key =os.environ['RAZORPAY_SECRET']

PAYMENT_VARIANTS = {
    "razorpay": (
        "django_payments_razorpay.RazorPayProvider",
        {"public_key": p_key, "secret_key": s_key},
    ),
}
CHECKOUT_PAYMENT_CHOICES = [('razorpay', 'RazorPay')]
