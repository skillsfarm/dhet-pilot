# dhet_app

A Django 5 starter with Tailwind CSS v4, Flowbite, HTMX, Alpine.js, and role-based access control.

## Stack

- **Backend**: Django 5.2, Django REST Framework, drf-spectacular
- **Frontend**: Tailwind CSS v4, Flowbite, HTMX, Alpine.js
- **Auth**: django-allauth with email-based authentication
- **Permissions**: django-role-permissions (5 roles: user, developer, content_manager, admin, super_admin)
- **Database**: PostgreSQL (configurable via DATABASE_URL)

## Features

- Email-based signup and login with mandatory verification
- New users default to "normal" role
- Role-based profile pages at `/<role>/profile/`
- Onboarding flow for normal users after first login
- Empty dashboard shell ready for customization
- API endpoints mirror UI permissions
- Auto-generated API docs at `/api/docs/` (Scalar)
- No build configuration required

## Quick Start

**Clone and setup environment**

```bash
cp .env.example .env  # Edit with your settings
```

**Install Python dependencies**

```bash
uv sync
```

**Install frontend dependencies**

```bash
pnpm install
```

**Build CSS**

```bash
pnpm run build
```

**Run migrations**

```bash
uv run python manage.py migrate
```

**Seed Database (Required)**

```bash
uv run python manage.py seed_roles        # Create role groups
uv run python manage.py seed_cookie_groups # Create default cookie groups
uv run python manage.py update_site       # Update Django Site name/domain
```

**Seed Optional Data**

```bash
uv run python manage.py seed_users        # Create dummy users (requires DEBUG=True)
uv run python manage.py seed_ofo          # Create OFO occupation data
```

**Create superuser**

```bash
uv run python manage.py createsuperuser
```

**Collect static files**

```bash
uv run python manage.py collectstatic --noinput
```

**Run development servers**

In one terminal (Frontend):

```bash
pnpm run dev
```

In another terminal (Backend):

```bash
uv run python manage.py runserver
```

## Project Structure

```text
dhet_app/
├── apps/                       # Django applications
│   ├── accounts/               # User authentication & profiles
│   │   ├── views.py            # UI views
│   │   ├── viewsets.py         # API viewsets
│   │   ├── serializers.py      # DRF serializers
│   │   ├── adapter.py          # Allauth customization
│   │   ├── forms.py            # Django forms
│   │   ├── models.py           # User-related models
│   │   ├── signals.py          # User signals
│   │   ├── admin.py            # Admin customization
│   │   └── management/         # Management commands
│   ├── candidates/             # Candidate management
│   ├── content/                # Content management
│   ├── core/                   # Core functionality
│   │   ├── models.py           # CuidModel base class
│   │   ├── views.py            # Common views
│   │   ├── middleware.py       # Request ID & logging middleware
│   │   ├── logging_config.py   # Logging configuration
│   │   ├── context_processors.py
│   │   └── management/         # Core management commands
│   ├── notifications/          # Notification system
│   └── storage/                # File storage utilities
├── dhet_app/                   # Django project config
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Root URL configuration
│   ├── roles.py                # Role definitions (RBAC)
│   ├── cookies.py              # Cookie consent config
│   ├── context_processors.py  # Global template context
│   ├── wsgi.py                 # WSGI entry point
│   └── asgi.py                 # ASGI entry point
├── templates/                  # HTML templates
│   ├── base.html               # Base template
│   ├── accounts/               # Account-related templates
│   ├── candidates/             # Candidate templates
│   ├── content/                # Content templates
│   ├── components/             # Reusable components
│   ├── layouts/                # Layout templates
│   ├── cookie_consent/         # Cookie consent UI
│   └── admin/                  # Admin customizations
├── theme/                      # Frontend assets
│   ├── main.css                # Tailwind CSS entry
│   └── dist/                   # Built CSS/JS assets
├── static/                     # Static files (images, etc.)
├── staticfiles/                # Collected static files (production)
├── logs/                       # Application logs
│   ├── development.log
│   ├── testing.log
│   ├── production.log
│   └── errors.log
├── scalar/                     # API documentation theme
├── manage.py                   # Django management script
├── pyproject.toml              # Python dependencies (uv)
├── package.json                # Frontend dependencies (pnpm)
├── .env                        # Environment variables
└── .env.example                # Example environment config
```

## Roles and Permissions

### User (Normal)

- Can edit own profile
- Complete onboarding after signup
- Redirected to `/onboarding/` on first login

### Content Manager

- All user permissions
- Can create and edit content
- Can manage OFO occupations and skills

### Admin

- All content manager permissions
- Can manage users
- Can manage system configuration

### Super Admin

- All admin permissions
- Full system access
- Can edit system settings

## URL Routes

- `/` - Home
- `/accounts/login/` - Login
- `/accounts/signup/` - Signup
- `/dashboard` - Dashboard (all authenticated users)
- `/onboarding/` - Onboarding (normal users only)
- `/normal/profile/` - Normal user profile
- `/admin-profile/` - Admin profile
- `/super/profile/` - Super admin profile
- `/api/users/` - User API endpoint
- `/api/docs/` - API documentation (Scalar)
- `/admin/` - Django admin

## Essential Environment Variables

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL recommended for production)
DATABASE_URL=postgresql://user:password@localhost:5432/dhet_db

# Site Configuration
SITE_NAME="DHET"
SITE_DOMAIN=localhost:8000

# Email Configuration (Zoho recommended)
EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST=smtp.zoho.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=noreply@example.com
ACCOUNT_EMAIL_VERIFICATION=mandatory  # none, optional, mandatory

# Debugging and Profiling
ENABLE_DEBUG_TOOLBAR=False
ENABLE_SILK=False
```

## Database Setup

### PostgreSQL (Recommended)

1. Create a PostgreSQL database:

```bash
createdb dhet_db
```

1. Set DATABASE_URL in .env:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dhet_db
```

1. Install psycopg (included in dependencies)

### SQLite (Development Only)

For quick local development:

```env
DATABASE_URL=sqlite:///db.sqlite3
```

## Development

### Watch CSS changes

```bash
pnpm run dev
```

### Build CSS for production

```bash
pnpm run build
```

### Run Django development server

```bash
uv run python manage.py runserver
```

### Create migrations

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### Linting & Formatting

**Python (Ruff):**

```bash
uv run ruff format .  # Format code
uv run ruff check .   # Lint code
uv run ruff check . --fix  # Auto-fix issues
```

**Templates (djLint):**

```bash
uv run djlint templates/ --reformat  # Format templates
uv run djlint templates/             # Lint templates
```

## API

REST API endpoints mirror the same permissions as the UI. All endpoints require authentication.

- `GET /api/users/` - List users (superusers see all, others see only themselves)
- `GET /api/users/{id}/` - Retrieve user
- `PUT /api/users/{id}/` - Update user
- `PATCH /api/users/{id}/` - Partial update user

API documentation available at `/api/docs/` with interactive Scalar interface.

## Customization

### Add new roles

Edit `dhet_app/roles.py` and add role class:

```python
class CustomRole(AbstractUserRole):
    verbose_name = "Custom Role"
    available_permissions = {
        "custom_permission": True,
    }
```

### Add new permissions

Update role classes in `dhet_app/roles.py` with new permission keys.

### Change theme colors

Edit `theme/main.css` or configure Flowbite themes.
