"""
Django settings for zinda_store project.
FINAL FIXED FOR HOSTINGER VPS
"""
from pathlib import Path
import os
import environ

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, 'django-insecure-placeholder'),
    ALLOWED_HOSTS=(list, []),
    DB_NAME=(str, 'zinda_store_db'),
    DB_USER=(str, 'ameer'),
    DB_PASSWORD=(str, 'rootameer'),
    DB_HOST=(str, '127.0.0.1'),
    DB_PORT=(int, 3306),
    RAZORPAY_KEY_ID=(str, ''),
    RAZORPAY_KEY_SECRET=(str, ''),
    RAZORPAY_WEBHOOK_SECRET=(str, ''),
    JORA_API_KEY=(str, ''), 
    JORA_BASE_URL=(str, 'https://server2.jobzinda.com/api/v1'), 
    FRONTEND_URL=(str, 'https://zindastore.com'),
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')


ALLOWED_HOSTS = env('ALLOWED_HOSTS') if env('ALLOWED_HOSTS') else ["*"]

INSTALLED_APPS = [
    'dal','dal_select2','unfold','django.contrib.admin','django.contrib.auth',
    'django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages',
    'django.contrib.staticfiles','rest_framework','corsheaders',
    'core','catalog','inventory','cart','orders','payments','shipping','promotions','reviews','support','cms',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'zinda_store.urls'
WSGI_APPLICATION = 'zinda_store.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'OPTIONS': {'charset': 'utf8mb4','init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata' 
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========= CORS - FIXED =========
CORS_ALLOW_ALL_ORIGINS = False  
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "https://zindastore.com",
    "https://www.zindastore.com",
    "http://localhost:5173", 
    "http://127.0.0.1:5173",
    "https://zindastore.com",
    "https://www.zindastore.com",
]

CSRF_TRUSTED_ORIGINS = [
    "https://zindastore.com",
    "https://www.zindastore.com",
    "https://api.zindastore.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://zindastore.com",
    "https://www.zindastore.com",
]

# ========= APP CONFIGS =========
RAZORPAY_KEY_ID = env('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = env('RAZORPAY_KEY_SECRET')
JORA_BASE_URL = env('JORA_BASE_URL')
JORA_API_KEY = env('JORA_API_KEY') 
FRONTEND_URL = env('FRONTEND_URL')

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
    'DEFAULT_PARSER_CLASSES': ('rest_framework.parsers.JSONParser',),
}

if not DEBUG:
   SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
   USE_X_FORWARDED_HOST = True