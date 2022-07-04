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


DEBUG = os.getenv("DEBUG") == "TRUE"

UNDER_TEST = (len(sys.argv) > 1 and sys.argv[1] == "test") or "pytest" in sys.modules

S3_MOCK_ENDPOINT = None
if os.getenv("INTEGRATION_TEST") == "TRUE":
    S3_MOCK_ENDPOINT = "http://localstack:4566"
elif DEBUG and not UNDER_TEST:
    S3_MOCK_ENDPOINT = "http://localhost:4566"

load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!


ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(" ")

CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS]

# Application definition

INSTALLED_APPS = [
    "accessibility_monitoring_platform.apps.cases",
    "accessibility_monitoring_platform.apps.audits",
    "accessibility_monitoring_platform.apps.common",
    "accessibility_monitoring_platform.apps.dashboard",
    "accessibility_monitoring_platform.apps.users",
    "accessibility_monitoring_platform.apps.notifications",
    "accessibility_monitoring_platform.apps.comments",
    "accessibility_monitoring_platform.apps.reminders",
    "accessibility_monitoring_platform.apps.overdue",
    "accessibility_monitoring_platform.apps.reports",
    "accessibility_monitoring_platform.apps.s3_read_write",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "axes",
    "django_otp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_email",  # <- if you want email capability.
    "two_factor",
    "two_factor.plugins.email",  # <- if you want email capability.
]

AUTHENTICATION_BACKENDS = [
    # AxesBackend should be the first backend in the AUTHENTICATION_BACKENDS list.
    "axes.backends.AxesBackend",
    "django.contrib.auth.backends.ModelBackend",
]

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_otp.middleware.OTPMiddleware",
    # AxesMiddleware should be the last middleware in the MIDDLEWARE list.
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "accessibility_monitoring_platform.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accessibility_monitoring_platform.apps.common.context_processors.platform_page",
            ],
            "builtins": [
                "accessibility_monitoring_platform.apps.common.templatetags.common_tags"
            ],
        },
    },
]


DATABASES = {}

if UNDER_TEST:
    DATABASES["default"] = {
        "NAME": "accessibility_monitoring_app",
        "ENGINE": "django.db.backends.sqlite3",
    }
    DATABASES["aws-s3-bucket"] = {
        "aws_access_key_id": "key",
        "aws_region": "us-east-1",
        "aws_secret_access_key": "secret",
        "bucket_name": "bucketname",
        "deploy_env": "",
    }
else:
    json_acceptable_string = os.getenv("VCAP_SERVICES", "").replace("'", '"')
    vcap_services = json.loads(json_acceptable_string)

    DATABASES["default"] = dj_database_url.parse(
        vcap_services["postgres"][0]["credentials"]["uri"]
    )

    DATABASES["aws-s3-bucket"] = vcap_services["aws-s3-bucket"][0]["credentials"]


DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = "Europe/London"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/


LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "dashboard:home"
LOGIN_URL = "two_factor:login"


STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

STATICFILES_DIRS = [BASE_DIR / "static/compiled/"]

STATIC_URL = os.path.join(BASE_DIR, "/static/")
STATIC_ROOT = os.path.join(BASE_DIR, "static/dist")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

CONTACT_ADMIN_EMAIL = (
    "accessibility-monitoring-platform-contact-form@digital.cabinet-office.gov.uk"
)

DEFAULT_FROM_EMAIL = (
    "accessibility-monitoring-platform-contact-form@digital.cabinet-office.gov.uk"
)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DATE_FORMAT = "d/m/Y"

MARKDOWN_EXTENSIONS = ["fenced_code"]

# django-axes
AXES_ONLY_USER_FAILURES = True  # Block only on username

if UNDER_TEST:
    #  django-axes is incompatible with the platform test environment
    INSTALLED_APPS.remove("axes")
    AUTHENTICATION_BACKENDS.remove("axes.backends.AxesBackend")
    MIDDLEWARE.remove("axes.middleware.AxesMiddleware")


TWO_FACTOR_REMEMBER_COOKIE_AGE = 60 * 60 * 24 * 6 # 2FA expires after 6 days
