"""
ASGI config for zinda_store project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

# Ensure PyMySQL is used as MySQLdb when running under ASGI
try:
    import pymysql  # type: ignore
    pymysql.install_as_MySQLdb()
except Exception:
    pass

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zinda_store.settings')

application = get_asgi_application()
