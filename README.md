# OmniRead

OmniRead is a Django bookstore for DRM-free ebooks. The Project Development 2
feature is **Shopping Cart and Order Review**. Readers can browse available
titles, add ebooks, edit their selection, remove titles, and review the current
total in Philippine pesos. Django saves each reader's cart in PostgreSQL.
Administrators use their existing dashboard and cannot access the reader cart.

## Run locally

Create a virtual environment with Python 3.12 and install the requirements.
Commands below use PowerShell.

```powershell
py -3.12 -m venv .venv
$python = ".\.venv\Scripts\python.exe"
& $python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and `DATABASE_URL` in `.env`.
Use a PostgreSQL connection URL from your own Supabase project. If your local
copy already uses `.env.local`, Django can load it as a fallback. Shell
environment variables take precedence over both files. Keep both files private.

```powershell
& $python manage.py migrate
& $python manage.py runserver
```

Open http://127.0.0.1:8000, sign up as a reader, and open **Explore Books**.

## Load demo ebooks

On a development database, use a PDF you have permission to distribute.
Keep it outside the public static directory.

```powershell
& $python manage.py seed_cart_demo --pdf "C:\path\to\demo.pdf"
```

Add Demo Ebook A and B to see **PHP 348.00**. Use **Edit selection** to
uncheck A and see **PHP 199.00**. Sign out and back in to confirm B persists.
Remove B to see the empty cart. A second reader starts with an independent cart.

## Run the tests

Use a disposable PostgreSQL instance or test database server. Django creates a
temporary test database and needs a database user with permission to create it.

```powershell
$env:DATABASE_URL = "postgresql://test_user:test_password@127.0.0.1:5432/postgres"
& $python manage.py test cart
```

Tests cover registration, login, profile editing, logout and dashboards, plus
cart persistence, role restrictions, cross-account isolation, unavailable
titles, duplicate adds, and stale edits.
