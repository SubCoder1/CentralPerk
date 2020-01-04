import os
from configparser import RawConfigParser

config = RawConfigParser()
config.read('/etc/centralperk/settings.ini')

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

CORS_ORIGIN_ALLOW_ALL = True
#CSRF_COOKIE_DOMAIN = None
#CSRF_COOKIE_SECURE = False
#SESSION_COOKIE_SECURE = False
SESSION_COOKIE_AGE = 480
SESSION_EXPIRE_AT_BROWSER_CLOSE = True # If a logged-in user closes the browser, session gets expired
SESSION_SAVE_EVERY_REQUEST = True # whenever you occur new request, It saves the session and updates timeout to expire
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = "default"

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = config.get('section', 'SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost', str(config.get('section', 'IP')), 'centralperk.social']
INTERNAL_IPS = ['127.0.0.1',]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'channels',

    #third party
    #'debug_toolbar',
    'corsheaders',
    'django_extensions',
    'storages',
    
    #own
    'AUth',
    'Profile',
    'Home',
]

AUTH_USER_MODEL = 'Profile.User'    # Custom User model is used

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'centralperk.middleware.login_required_middleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'centralperk.urls'

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

WSGI_APPLICATION = 'centralperk.wsgi.application'

# Channels
ASGI_APPLICATION = "centralperk.routing.application"
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [config.get('section', 'REDIS_URL')],
        },
    },
}


PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.Argon2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
        'django.contrib.auth.hashers.BCryptPasswordHasher',
        'django.contrib.auth.hashers.SHA1PasswordHasher',
        'django.contrib.auth.hashers.MD5PasswordHasher',
        'django.contrib.auth.hashers.CryptPasswordHasher',
)


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'centralperk',
    "USER": str(config.get('section', 'DB_USER')),
    "PASSWORD": str(config.get('section', 'DB_PASS')),
    "HOST": 'localhost',
    "PORT": '5432',
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": str(config.get('section', 'REDIS_URL') + "/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "example"
    }
}

# CELERY STUFF
BROKER_URL = config.get('section', 'REDIS_URL')
CELERY_RESULT_BACKEND = config.get('section', 'REDIS_URL')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Max size of post file upload
DATA_UPLOAD_MAX_MEMORY_SIZE = 31457280

import mimetypes
# Additional MIME Types for web fonts
mimetypes.add_type("application/font-woff2", ".woff2", strict=True)
mimetypes.add_type("application/font-woff", ".woff", strict=True)
mimetypes.add_type("application/vnd.ms-fontobject", ".eot", strict=True)
mimetypes.add_type("application/x-font-opentype", ".otf", strict=True)
mimetypes.add_type("application/x-font-ttf", ".ttf", strict=True)
mimetypes.add_type("image/svg+xml", ".svg", strict=True)
# HTML5 video webm support
mimetypes.add_type("video/webm", ".webm", strict=True)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATICFILES_STORAGE = 'centralperk.storage.WhiteNoiseStaticFilesStorage'

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Absolute filesystem path to the directory that will hold user-uploaded files.
# AWS S3 settings
AWS_ACCESS_KEY_ID = config.get('aws', 'AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config.get('aws', 'AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config.get('aws', 'AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = config.get('aws', 'AWS_S3_CUSTOM_DOMAIN')
AWS_S3_OBJECT_PARAMETERS = {    
    'CacheControl': 'max-age=86400',
}

DEFAULT_FILE_STORAGE = 'centralperk.storage.MediaStorage'

ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
AWS_DEFAULT_ACL = None


# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home2/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# URL that handles the media served from MEDIA_ROOT.
MEDIA_URL = '/media/'

LOGIN_URL  = '/'

LOGIN_EXEMPT_URL = [
    '/register/',
    '/',
]
