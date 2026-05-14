#!/usr/bin/env sh
set -eu

python manage.py migrate --noinput
python manage.py seed_roles
python manage.py seed_cookie_groups
python manage.py update_site

if [ "${SEED_DEMO_DATA:-false}" = "true" ]; then
    python manage.py seed_users
    python manage.py seed_ofo
fi

python manage.py collectstatic --noinput

exec "$@"
