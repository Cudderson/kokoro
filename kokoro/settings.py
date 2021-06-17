"""
Django settings for kokoro project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import warnings

# Access env variables
load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# Load Django Secret Key from environment variables
SECRET_KEY = os.getenv('KOKORO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
]


# Application definition

INSTALLED_APPS = [
    # My Apps
    'kokoro_app',
    # Need to include config path for signals to work
    'users.apps.UsersConfig',

    # including config path for signals
    'notifications.apps.NotificationsConfig',

    # django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

ROOT_URLCONF = 'kokoro.urls'

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
                # context processor that retrieves notifications for user
                'notifications.context_processors.pass_notifications_to_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'kokoro.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': 'C:\ProgramData\MySQL\MySQL Server 8.0\my.ini',
            'isolation_level': 'read committed',
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

# for prod
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'media'),
]

STATIC_URL = '/static/'

# Location where uploaded media files will be located on file system
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Where to access in browser
MEDIA_URL = '/media/'

# My settings
LOGIN_URL = 'users:login'

# Email Setup

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('KOKORO_EMAIL_HOST')
EMAIL_USE_TLS = True
EMAIL_PORT = os.environ.get('KOKORO_EMAIL_PORT')
EMAIL_HOST_USER = os.environ.get('KOKORO_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('KOKORO_EMAIL_HOST_PASSWORD')

EMAIL_VARS = [
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_HOST_USER,
    EMAIL_HOST_PASSWORD
]

EMAIL_SETUP_SUCCESSFUL = True

print('Retrieving Email Setup variables...')
for email_var in EMAIL_VARS:
    if not email_var:
        EMAIL_SETUP_SUCCESSFUL = False

if EMAIL_SETUP_SUCCESSFUL:
    print('Email Setup Successful!')
else:
    print("ERROR: Couldn't retrieve email setup variables")

warnings.filterwarnings(
    'error', r"DateTimeField .* received a naive datetime",
    RuntimeWarning, r'django\.db\.models\.fields',
)

# heroku settings
import django_heroku
django_heroku.settings(locals())
