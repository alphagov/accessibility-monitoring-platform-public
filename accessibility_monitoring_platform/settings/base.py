"""
Django settings for accessibility_monitoring_platform project.

Generated by 'django-admin startproject' using Django 3.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
import dj_database_url
import sys
import os
import json
from dotenv import load_dotenv

UNDER_TEST = (len(sys.argv) > 1 and sys.argv[1] == 'test')

load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if os.getenv('DEBUG') == 'TRUE' else False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(' ')

# Application definition

INSTALLED_APPS = [
    'accessibility_monitoring_platform.apps.axe_data',
    'accessibility_monitoring_platform.apps.dashboard',
    'accessibility_monitoring_platform.apps.query_local_website_registry',
    'accessibility_monitoring_platform.apps.users',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'accessibility_monitoring_platform.urls'

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


DATABASES = {}

if UNDER_TEST:
    DATABASES['default'] = {'NAME': 'accessibility_monitoring_app', 'ENGINE': 'django.db.backends.sqlite3'}
    DATABASES['accessibility_domain_db'] = {'NAME': 'domain_register', 'ENGINE': 'django.db.backends.sqlite3'}
    DATABASES['axe_data'] = {'NAME': 'axe_data', 'ENGINE': 'django.db.backends.sqlite3'}
else:
    json_acceptable_string = os.getenv('VCAP_SERVICES').replace('\'', '\"')
    db = json.loads(json_acceptable_string)

    d = {
        'monitoring-platform-default-db': None,
        'a11ymon-postgres': None,
        'axeresults-postgres': None,
    }
    # DATABASE_NAMES = []

    for i in db['postgres']:
        d[i['name']] = i['credentials']['uri'] if i['name'] in d.keys() else None

    DATABASES['default'] = dj_database_url.parse(d['monitoring-platform-default-db'])
    DATABASES['accessibility_domain_db'] = dj_database_url.parse(d['a11ymon-postgres'])
    DATABASES['accessibility_domain_db']['OPTIONS'] = {'options': '-c search_path=pubsecweb,public'}
    DATABASES['axe_data'] = dj_database_url.parse(d['axeresults-postgres'])
    DATABASES['axe_data']['OPTIONS'] = {'options': '-c search_path=a11ymon,public'}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/


LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'dashboard:home'


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)

STATICFILES_DIRS = [BASE_DIR / 'static/compiled/']

STATIC_URL = os.path.join(BASE_DIR, '/static/')
STATIC_ROOT = os.path.join(BASE_DIR, 'static/dist')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
