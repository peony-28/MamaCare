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
    from django.contrib.auth.models import User
    
    # Run migrations on startup to ensure database exists
    print("Running database migrations on startup...", file=sys.stderr)
    execute_from_command_line(['manage.py', 'migrate', '--run-syncdb', '--noinput'])
    
    # Create admin user if it doesn't exist (for Render's ephemeral filesystem)
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@mamacare.com')
    
    if not User.objects.filter(username=admin_username).exists():
        print(f"Creating admin user '{admin_username}' on startup...", file=sys.stderr)
        User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password
        )
        print(f"Admin user '{admin_username}' created successfully!", file=sys.stderr)
    else:
        print(f"Admin user '{admin_username}' already exists.", file=sys.stderr)
        
except Exception as e:
    # Log but don't fail - migrations should have run during build
    print(f"Warning: Could not initialize database on startup: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)

application = get_wsgi_application()

