"""
Django settings for zinda_store project.
"""
from pathlib import Path
from decouple import config
import os
import environ

# Ensure PyMySQL is used as MySQLdb for Django's MySQL backend
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables
env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, 'django-insecure-placeholder'),
    ALLOWED_HOSTS=(list, []),
    DB_NAME=(str, 'zinda_store_db'),
    DB_USER=(str, 'root'),
    DB_PASSWORD=(str, 'pass123'),
    DB_HOST=(str, '127.0.0.1'),
    DB_PORT=(int, 33306),
    RAZORPAY_KEY_ID=(str, ''),
    RAZORPAY_KEY_SECRET=(str, ''),
    RAZORPAY_WEBHOOK_SECRET=(str, ''),
    JORA_API_KEY=(str, ''), # ITHU ADD CHEYYU
    JORA_BASE_URL=(str, 'https://server2.jobzinda.com/api/v1'), # ITHU KODI
    FRONTEND_URL=(str, 'http://localhost:5173'), # React/Vite url
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

# PRODUCTION IL ITHU MAATTU
ALLOWED_HOSTS = env('ALLOWED_HOSTS')
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.vercel.app', '.railway.app', '.pythonanywhere.com'] # nee host cheyyunna domain

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'core',
    'catalog',
    'inventory',
    'cart',
    'orders',
    'payments',
    'shipping',
    'promotions',
    'reviews',
    'support',
    'cms',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # CORS should be top
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # ADD THIS for static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'zinda_store.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'zinda_store.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata' # CHANGED to IST
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' # ADD for prod

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS SETTINGS - IMPORTANT
CORS_ALLOW_ALL_ORIGINS = False # PROD IL TRUE VENDANAM
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173", # Vite/React
    "http://localhost:3000", # NextJS
    env('FRONTEND_URL'), # .env ninnu
]
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

# Currency configuration
DEFAULT_CURRENCY = 'INR'

# Razorpay configuration
RAZORPAY_KEY_ID = env('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = env('RAZORPAY_KEY_SECRET')
RAZORPAY_WEBHOOK_SECRET = env('RAZORPAY_WEBHOOK_SECRET')

# JobzInda Config
JORA_BASE_URL = env('JORA_BASE_URL')
JORA_API_KEY = env('JORA_API_KEY') # ITHU ILLATHATHU KONDU ANU ERROR VARUNNATHU

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
    'DEFAULT_PARSER_CLASSES': ('rest_framework.parsers.JSONParser',),
}

# Security for Production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


UNFOLD = {
    'SITE_TITLE': 'Zinda Store Admin',
    'SITE_HEADER': 'Zinda Store',
    "SITE_LOGO": "/static/branding/logo.png",
    # Load custom CSS to tweak input borders/appearance
    "STYLES": [
        "/static/branding/admin-overrides.css",
    ],
    "SIDEBAR": {
        "show_search": True,
        "navigation": [
            {
                "title": "Dashboard",
                "items": [
                    {
                        "title": "Overview",
                        "icon": "space_dashboard",
                        "link": "/admin/",
                    },
                ],
            },
            {
                "title": "Authentication & Authorization",
                "collapsible": True,
                "items": [
                    {
                        "title": "Groups",
                        "icon": "group",
                        "link": "/admin/auth/group/",
                    },
                    {
                        "title": "Users",
                        "icon": "person",
                        "link": "/admin/auth/user/",
                    },
                ],
            },
            {
                "title": "Catalog",
                "collapsible": True,
                "items": [
                    {
                        "title": "Brands",
                        "icon": "store",
                        "link": "/admin/catalog/brand/",
                    },
                    {
                        "title": "Categories",
                        "icon": "category",
                        "link": "/admin/catalog/category/",
                    },
                    {
                        "title": "Product images",
                        "icon": "photo_library",
                        "link": "/admin/catalog/productimage/",
                    },
                    {
                        "title": "Product variants",
                        "icon": "widgets",
                        "link": "/admin/catalog/productvariant/",
                    },
                    {
                        "title": "Products",
                        "icon": "inventory_2",
                        "link": "/admin/catalog/product/",
                    },
                ],
            },
            {
                "title": "CMS",
                "collapsible": True,
                "items": [
                    {
                        "title": "Banners",
                        "icon": "collections_bookmark",
                        "link": "/admin/cms/banner/",
                    },
                    {
                        "title": "Pages",
                        "icon": "description",
                        "link": "/admin/cms/page/",
                    },
                ],
            },
            {
                "title": "Inventory",
                "collapsible": True,
                "items": [
                    {
                        "title": "Warehouses",
                        "icon": "warehouse",
                        "link": "/admin/inventory/warehouse/",
                    },
                    {
                        "title": "Inventory items",
                        "icon": "inventory",
                        "link": "/admin/inventory/inventoryitem/",
                    },
                    {
                        "title": "Stock movements",
                        "icon": "sync_alt",
                        "link": "/admin/inventory/stockmovement/",
                    },
                ],
            },
            {
                "title": "Cart",
                "collapsible": True,
                "items": [
                    {
                        "title": "Carts",
                        "icon": "shopping_cart",
                        "link": "/admin/cart/cart/",
                    },
                ],
            },
            {
                "title": "Orders",
                "collapsible": True,
                "items": [
                    {
                        "title": "Orders",
                        "icon": "receipt_long",
                        "link": "/admin/orders/order/",
                    },
                    {
                        "title": "Invoices",
                        "icon": "request_quote",
                        "link": "/admin/orders/invoice/",
                    },
                ],
            },
            {
                "title": "Payments",
                "collapsible": True,
                "items": [
                    {
                        "title": "Payment intents",
                        "icon": "payments",
                        "link": "/admin/payments/paymentintent/",
                    },
                    {
                        "title": "Refunds",
                        "icon": "undo",
                        "link": "/admin/payments/refund/",
                    },
                ],
            },
            {
                "title": "Shipping",
                "collapsible": True,
                "items": [
                    {
                        "title": "Shipping methods",
                        "icon": "local_shipping",
                        "link": "/admin/shipping/shippingmethod/",
                    },
                    {
                        "title": "Shipments",
                        "icon": "move_up",
                        "link": "/admin/shipping/shipment/",
                    },
                    {
                        "title": "Shipment items",
                        "icon": "inventory_2",
                        "link": "/admin/shipping/shipmentitem/",
                    },
                ],
            },
            {
                "title": "Promotions",
                "collapsible": True,
                "items": [
                    {
                        "title": "Coupons",
                        "icon": "loyalty",
                        "link": "/admin/promotions/coupon/",
                    },
                ],
            },
            {
                "title": "Reviews",
                "collapsible": True,
                "items": [
                    {
                        "title": "Reviews",
                        "icon": "reviews",
                        "link": "/admin/reviews/review/",
                    },
                ],
            },
            {
                "title": "Support",
                "collapsible": True,
                "items": [
                    {
                        "title": "Return requests",
                        "icon": "support_agent",
                        "link": "/admin/support/returnrequest/",
                    },
                ],
            },
        ],
    },

    "LOGIN": {
        # Shown on the login screen (logo)
        "LOGO": "/static/branding/logo.png",
        # Optional illustration/image on login page
        # "IMAGE": "/static/branding/login-illustration.svg",
        # Optional: title/intro text
        # "TITLE": "Welcome back",
        # "SUBTITLE": "Sign in to Zinda Store Admin",
    },
}
