from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "fallback-dev-key-change-in-production")
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true" # will be "false" for any other value
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [

    # Django's built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

   # third-party apps
    "rest_framework",

    # our app
    "core"
]

MIDDLEWARE = [

    # HTTPS redirects + security headers
    'django.middleware.security.SecurityMiddleware',

    # sessions with cookies
    'django.contrib.sessions.middleware.SessionMiddleware',

    # URL normalization
    'django.middleware.common.CommonMiddleware',

    # CSRF tokens
    'django.middleware.csrf.CsrfViewMiddleware',

    # attach authentication data to `request.user`
    'django.contrib.auth.middleware.AuthenticationMiddleware',

    # flash messages (used in the Django Admin pages)
    'django.contrib.messages.middleware.MessageMiddleware',

    # set the X-Frame-Options header to DENY 
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'memo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'memo.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/New_York"
USE_I18N = True
USE_TZ = True   # store datetimes in the database in UTC

STATIC_URL = 'static/'

