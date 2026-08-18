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
python manage.py runserver 0.0.0.0:8000
```

Open `http://127.0.0.1:8000` on the server computer. To access the project from
another computer on the same network, replace `127.0.0.1` with the server
computer's local IP address, for example `http://192.168.1.25:8000`.

On macOS, find the local IP with:

```bash
ipconfig getifaddr en0
```

If that returns no address and the Mac is connected over Wi-Fi or another
interface, try `ipconfig getifaddr en1`. Both computers must be on the same
network, and the macOS firewall must allow incoming connections to Python.

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
