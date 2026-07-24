# Zinda Store Backend

Django backend with Unfold admin UI, configured for MySQL, serving as backend for a future Flutter app.

## Quickstart

1. Create and activate venv (already created as `.venv` if you ran the setup commands):
```bash
python3 -m venv .venv
. .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# edit .env as needed
```

4. Create the database (MySQL) if it does not exist:
```sql
CREATE DATABASE zinda_store_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON zinda_store_db.* TO 'ameer'@'%' IDENTIFIED BY 'rootameer';
FLUSH PRIVILEGES;
```

5. Run migrations and start server:
```bash
python manage.py migrate
python manage.py createsuperuser  # optional, to access admin
python manage.py runserver
```

- Admin: http://127.0.0.1:8000/admin/
- Health: http://127.0.0.1:8000/api/health/

## Notes
- Admin UI uses `django-unfold`. You can customize titles via `UNFOLD` settings in `zinda_store/settings.py`.
- Environment variables are loaded via `django-environ`. Defaults exist in settings, but you should override with `.env`.
- MySQL driver is PyMySQL configured in `asgi.py` and `wsgi.py`.
