from pathlib import Path
import os

# base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# secret key - in production this should be set as environment variable
# never share this key publicly
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-+34t(^(+)p)8$9h2w7*%fq101w@2#@vd9kle9gl3m10pptgyu_')

# debug mode - set to False in production
# reads from environment variable, defaults to True for local development
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# allow all hosts for now - restrict this in production
ALLOWED_HOSTS = ['*']


# apps installed in this project
INSTALLED_APPS = [
    # default django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # my app
    'accounts',
]


# middleware - runs on every request/response
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # whitenoise serves static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',    # csrf protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'


# template settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # look for templates in root templates folder
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

WSGI_APPLICATION = 'myproject.wsgi.application'


# database settings - using sqlite3 for development
# for production should switch to postgresql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# password validation rules
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# language and timezone settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'  # india timezone
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# static files settings (css, js etc)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# whitenoise compresses and serves static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# media files settings (user uploaded images)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# login settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'  # where to go after login

# store messages in session
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
