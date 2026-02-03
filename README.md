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

1. **Clone and setup environment**

```bash
cp .env.example .env  # Edit with your settings
```

1. **Install Python dependencies**

```bash
uv sync
```

1. **Install frontend dependencies**

```bash
pnpm install
```

1. **Build CSS**

```bash
pnpm run build
```

1. **Run migrations**

```bash
uv run python manage.py migrate
```

1. **Seed Database (Required)**

```bash
uv run python manage.py seed_roles        # Create role groups
uv run python manage.py seed_cookie_groups # Create default cookie groups
uv run python manage.py update_site       # Update Django Site name/domain
```

1. **Seed Optional Data**

```bash
uv run python manage.py seed_users        # Create dummy users (requires DEBUG=True)
uv run python manage.py seed_ofo          # Create OFO occupation data
```

1. **Create superuser**

```bash
uv run python manage.py createsuperuser
```

1. **Collect static files**

```bash
uv run python manage.py collectstatic --noinput
```

1. **Run development servers**

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
├── dhet_app/          # Django config
│   ├── settings.py
│   ├── urls.py
│   ├── roles.py        # Role definitions
│   └── wsgi.py
├── users/              # User app
│   ├── views.py        # UI views
│   ├── viewsets.py     # API viewsets
│   ├── serializers.py
│   ├── adapter.py      # Allauth customization
│   └── forms.py
├── templates/
│   ├── base.html
│   └── users/
│       ├── dashboard.html
│       ├── onboarding.html
│       └── profile.html
├── theme/
│   ├── main.css        # Tailwind entry
│   └── dist/           # Built assets
├── manage.py
└── .env
```

## Roles and Permissions

### User (Normal)
- Can edit own profile
- Complete onboarding after signup
- Redirected to `/onboarding/` on first login

### Developer
- All user permissions
- Can manage technical content
- Access to developer tools

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

## Environment Variables

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

# S3 / Object Storage (Optional)
ACCESS_KEY_ID=""
SECRET_ACCESS_KEY=""
STORAGE_BUCKET_NAME=""
S3_ENDPOINT_URL="https://nyc3.digitaloceanspaces.com"
S3_REGION_NAME="nyc3"
S3_CUSTOM_DOMAIN=""  # Optional: Set if you have a custom domain or CDN

# Cookie Consent
COOKIE_CONSENT_ENABLED=False

# Notifications
NOTIFICATION_TEST_EMAIL=""
```

## Database Setup

### PostgreSQL (Recommended)

1. Create a PostgreSQL database:
```bash
createdb dhet_db
```

2. Set DATABASE_URL in .env:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/dhet_db
```

3. Install psycopg (included in dependencies)

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
