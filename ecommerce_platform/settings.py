from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6!q)nx(+w5g1f=^@nzg+@*9iw9o5xvc0in!t!u%(5gksk#l#&l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://1a1b-125-22-172-170.ngrok-free.app',
    # Add other trusted origins if needed
]

CORS_ALLOWED_ORIGINS = [
    'https://1a1b-125-22-172-170.ngrok-free.app',  # Replace with your ngrok URL
]

CSRF_COOKIE_SECURE = True  # For testing only (change to True in production with HTTPS)
SESSION_COOKIE_SECURE = True


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    # Third-party apps
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',  # For JWT blacklisting
    'django_celery_beat',  # For Celery task scheduling
    'django_celery_results',  # To store task results
    'razorpay',
    # Custom apps
    'authusers',
    'vendors',
    'products',
    'customer',
    'cart_orders',
    "commission_and_calculations",
    "admin_portal",
    "banners",
    
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecommerce_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Ensure templates directory is specified
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


WSGI_APPLICATION = 'ecommerce_platform.wsgi.application'

# Database
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
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication settings
AUTH_USER_MODEL = 'authusers.User'

# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # Default for other endpoints
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# Simple JWT configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=999),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=100),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': True,
}

# Celery configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'django-db'
from datetime import timedelta

CELERY_BEAT_SCHEDULE = {
    # Existing tasks
    'delete_expired_temp_users': {
        'task': 'authusers.tasks.delete_expired_temp_users',
        'schedule': timedelta(minutes=1),  # Run every minute
    },
    # New task for deleting stale orders
    'delete_stale_orders_every_5_minutes': {
        'task': 'cart_orders.tasks.delete_stale_orders',
        'schedule': timedelta(minutes=1),  # Run every 5 minutes
    },
}




from decouple import config
# EMAIL CONFIGURATION
# =====================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}



CELERY_TASK_ALWAYS_EAGER = True
CELERY_IMPORTS = ('authusers.tasks',)


CORS_ALLOW_ALL_ORIGINS = True


CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]



BASE_URL = "http://127.0.0.1:8000"


RAZORPAY_KEY_ID = "rzp_test_EVswR8OHh71h2F"
RAZORPAY_KEY_SECRET = "PY7vpZUFrdPBupe01k8fJb7F"

RAZORPAY_WEBHOOK_SECRET = "55f04bd6630ed2436e58cbd0b791a442ac13dc3f9d969069b42558528820a561"