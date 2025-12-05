"""
Django settings for mamacare_project project.
"""

from pathlib import Path
import os
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production-!@#$%^&*()')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# ALLOWED_HOSTS configuration
# For Render deployment, automatically include .onrender.com domains
allowed_hosts_default = 'localhost,127.0.0.1'

# Check for Render environment variables first
render_external_url = os.environ.get('RENDER_EXTERNAL_URL', '')
render_service_name = os.environ.get('RENDER_SERVICE_NAME', '')

# Build allowed hosts list
allowed_hosts_list = []

# Add explicitly configured hosts
if config('ALLOWED_HOSTS', default=None):
    allowed_hosts_list.extend([h.strip() for h in config('ALLOWED_HOSTS').split(',') if h.strip()])

# Auto-detect from Render environment
if render_external_url:
    from urllib.parse import urlparse
    parsed = urlparse(render_external_url)
    if parsed.netloc:
        allowed_hosts_list.append(parsed.netloc)
elif render_service_name:
    allowed_hosts_list.append(f'{render_service_name}.onrender.com')

# Add defaults if nothing else was found
if not allowed_hosts_list:
    allowed_hosts_list = [h.strip() for h in allowed_hosts_default.split(',') if h.strip()]

ALLOWED_HOSTS = list(set(allowed_hosts_list))  # Remove duplicates


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'predictions',  # Our main app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # For static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mamacare_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'mamacare_project.wsgi.application'


# Database - MongoDB Configuration
# Using PyMongo directly instead of djongo for better compatibility

MONGODB_SETTINGS = {
    'host': config('MONGODB_HOST', default='mongodb://localhost:27017/'),
    'name': config('MONGODB_NAME', default='mamacare_db'),
    'username': config('MONGODB_USERNAME', default=''),
    'password': config('MONGODB_PASSWORD', default=''),
}

# For Django's default SQLite (used for auth, sessions, etc.)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# WhiteNoise configuration for static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Security Settings (for production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# ML Models Path
ML_MODELS_DIR = BASE_DIR / 'ml_models'

