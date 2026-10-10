# Zinda Store Backend

Django backend with Unfold admin UI, configured for MySQL/SQLite, serving as the backend for the store and Flutter app.

## Quickstart (Windows / Linux)

### 1. Prerequisites
- **Python 3.10 - 3.12** installed and added to your `PATH`.
- (Optional) **MySQL** installed if running with MySQL database (or use SQLite for zero-setup local dev).

### 2. Create and Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(If script execution is disabled in PowerShell, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first, or use Command Prompt: `.\.venv\Scripts\activate.bat`)*

**On Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
> **Note for Windows:** If `mysqlclient` fails during installation because of missing C++ build tools, simply install PyMySQL (`pip install pymysql`) which is already configured in the project to emulate MySQLdb.

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
# Windows PowerShell:
Copy-Item .env.example .env

# Linux / Git Bash:
cp .env.example .env
```

**Choose your Database Mode in `.env`:**
- **Option A (Zero Setup - SQLite):** Add `USE_SQLITE=True` in your `.env` file. No MySQL server needed!
- **Option B (MySQL - Production Parity):** Keep `USE_SQLITE=False` (default) and ensure MySQL is running with database `zinda_store_db`:
  ```sql
  CREATE DATABASE zinda_store_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  ```
  Set your MySQL credentials (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) in `.env`.

### 5. Run Migrations & Start Server
```bash
python manage.py migrate
python manage.py createsuperuser  # Create your admin credentials
python manage.py runserver
```

### 6. Endpoints
- **Admin Panel:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Health Check:** [http://127.0.0.1:8000/api/core/health/](http://127.0.0.1:8000/api/core/health/)
- **Products API:** [http://127.0.0.1:8000/api/products/](http://127.0.0.1:8000/api/products/)
- **Categories API:** [http://127.0.0.1:8000/api/categories/](http://127.0.0.1:8000/api/categories/)
- **Cart API:** [http://127.0.0.1:8000/api/cart/](http://127.0.0.1:8000/api/cart/)

## Notes
- Admin UI uses `django-unfold`.
- Environment variables are loaded via `django-environ`.
- MySQL driver is `PyMySQL` configured in `asgi.py`, `wsgi.py`, and `settings.py`.
