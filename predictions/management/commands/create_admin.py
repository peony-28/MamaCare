"""
Management command to create admin user from environment variables
Usage: python manage.py create_admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = 'Create admin user from environment variables or default credentials'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Admin username (default: admin)',
            default=os.environ.get('ADMIN_USERNAME', 'admin')
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Admin email',
            default=os.environ.get('ADMIN_EMAIL', 'admin@mamacare.com')
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Admin password (or set ADMIN_PASSWORD env var)',
            default=os.environ.get('ADMIN_PASSWORD', None)
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password'] or os.environ.get('ADMIN_PASSWORD', 'admin123')

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists. Skipping creation.')
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created superuser "{username}"')
        )
        self.stdout.write(
            self.style.WARNING(f'⚠️  Please change the default password after first login!')
        )

