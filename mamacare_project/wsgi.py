"""
WSGI config for mamacare_project project.
"""

import os
import sys

# Set Django settings before importing anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mamacare_project.settings')

# Import Django after setting environment
import django
django.setup()

# Now import Django components
from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import connection

# Ensure database is initialized before starting (for Render's ephemeral filesystem)
def initialize_database():
    """Initialize database tables and create admin user"""
    try:
        # Check if database file exists, create it if needed
        from django.conf import settings
        db_path = str(settings.DATABASES['default']['NAME'])
        
        # Ensure directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # Run migrations
        print("=" * 60, file=sys.stderr)
        print("Initializing database on startup...", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        
        # Use call_command instead of execute_from_command_line for better reliability
        call_command('migrate', verbosity=2, interactive=False, run_syncdb=True)
        
        print("✓ Database migrations completed", file=sys.stderr)
        
        # Create admin user if it doesn't exist
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@mamacare.com')
        
        if not User.objects.filter(username=admin_username).exists():
            print(f"Creating admin user '{admin_username}'...", file=sys.stderr)
            User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password
            )
            print(f"✓ Admin user '{admin_username}' created successfully!", file=sys.stderr)
        else:
            print(f"✓ Admin user '{admin_username}' already exists.", file=sys.stderr)
        
        print("=" * 60, file=sys.stderr)
        print("Database initialization complete!", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        
    except Exception as e:
        # Log error but don't fail startup - app will still run
        print("=" * 60, file=sys.stderr)
        print(f"ERROR: Database initialization failed: {e}", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print("WARNING: Application will start but login/registration may not work!", file=sys.stderr)
        print("=" * 60, file=sys.stderr)

# Initialize database on module import
initialize_database()

# Now get the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

