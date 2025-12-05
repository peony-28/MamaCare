"""
WSGI config for mamacare_project project.
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mamacare_project.settings')

# Ensure database is initialized before starting (for Render's ephemeral filesystem)
try:
    from django.core.management import execute_from_command_line
    # Run migrations on startup to ensure database exists
    execute_from_command_line(['manage.py', 'migrate', '--run-syncdb', '--noinput'])
except Exception as e:
    # Log but don't fail - migrations should have run during build
    print(f"Warning: Could not run migrations on startup: {e}", file=sys.stderr)

application = get_wsgi_application()

