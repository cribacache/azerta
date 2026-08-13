# Django Project Starter

A scalable, production-ready Django starter scaffolded with best practices.

## Project Structure

```text
django_project/
├── .venv/                   # Isolated virtual environment
├── .env                     # Local environment secrets & settings
├── .env.example             # Example environment configuration
├── .gitignore               # Comprehensive Python/Django ignore rules
├── requirements.txt         # Pinned project dependencies
├── manage.py                # Django CLI management script
├── config/                  # Core configuration package
│   ├── settings.py          # Environment-driven settings
│   ├── urls.py              # Root URL routing
│   ├── asgi.py
│   └── wsgi.py
├── apps/                    # Pluggable Django applications
│   └── accounts/            # Custom User model & auth
├── templates/               # Global templates
│   ├── base.html            # Base layout
│   └── home.html            # Starter landing page
├── static/                  # Static assets
│   └── css/
│       └── style.css        # Clean UI styling
└── media/                   # User-uploaded files
```

---

## Quick Start

### 1. Activate the Virtual Environment

```bash
source .venv/bin/activate
```

### 2. Run Database Migrations

```bash
python manage.py migrate
```

### 3. Create a Superuser

```bash
python manage.py createsuperuser
```

### 4. Start the Development Server

```bash
python manage.py runserver 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## Adding New Apps

To create a new app organized inside the `apps/` directory:

```bash
mkdir apps/articles
python manage.py startapp articles apps/articles
```

Remember to:
1. Set `name = 'apps.articles'` in `apps/articles/apps.py`.
2. Add `'apps.articles'` to `INSTALLED_APPS` in `config/settings.py`.
3. Create migrations with `python manage.py makemigrations articles`.

---

## Running Tests

```bash
python manage.py test
```
