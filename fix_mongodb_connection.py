"""
Diagnose and fix MongoDB Atlas connection issues
"""
import os
import sys
import django
from urllib.parse import quote_plus

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mamacare_project.settings')
django.setup()

from django.conf import settings
from pymongo import MongoClient

print("=" * 70)
print("MongoDB Connection Diagnostic & Fix")
print("=" * 70)

mongodb_config = settings.MONGODB_SETTINGS
connection_string = mongodb_config['host']

print(f"\n📋 Current Configuration:")
print(f"   Host: {connection_string[:50]}...")
print(f"   Database: {mongodb_config['name']}")
print(f"   Username (separate): {mongodb_config.get('username', '(not set)')}")
print(f"   Password (separate): {'***' if mongodb_config.get('password') else '(not set)'}")

# Check if connection string has credentials
has_creds_in_string = '@' in connection_string

print(f"\n🔍 Analysis:")
if has_creds_in_string:
    print(f"   ✓ Connection string already has credentials embedded")
    # Extract username and password from connection string for testing
    try:
        if 'mongodb+srv://' in connection_string:
            parts = connection_string.replace('mongodb+srv://', '').split('@')
            if len(parts) == 2:
                creds = parts[0].split(':')
                if len(creds) == 2:
                    username_from_string = creds[0]
                    password_from_string = creds[1]
                    print(f"   Username in string: {username_from_string}")
                    print(f"   Password in string: {'*' * len(password_from_string)}")
    except:
        pass
else:
    print(f"   ⚠ Connection string doesn't have credentials")
    print(f"   Will use MONGODB_USERNAME and MONGODB_PASSWORD if set")

# Test different connection string formats
print(f"\n🧪 Testing Connection Formats...")

# Format 1: Use connection string as-is
print(f"\n1️⃣ Testing: Connection string as-is")
try:
    client = MongoClient(connection_string, serverSelectionTimeoutMS=10000)
    client.admin.command('ping')
    db = client[mongodb_config['name']]
    print(f"   ✅ SUCCESS with original format!")
    print(f"   Database: {db.name}")
    client.close()
    sys.exit(0)
except Exception as e:
    print(f"   ❌ Failed: {str(e)[:100]}")

# Format 2: Add database name to path if missing
if '/?' in connection_string or connection_string.endswith('/'):
    print(f"\n2️⃣ Testing: Adding database name to connection string")
    try:
        # Remove trailing / and query params, add database name
        base_conn = connection_string.split('?')[0].rstrip('/')
        if '/' not in base_conn.split('@')[-1]:
            # No database in path, add it
            new_conn = f"{base_conn}/{mongodb_config['name']}?retryWrites=true&w=majority"
        else:
            new_conn = f"{base_conn}?retryWrites=true&w=majority"
        
        client = MongoClient(new_conn, serverSelectionTimeoutMS=10000)
        client.admin.command('ping')
        db = client[mongodb_config['name']]
        print(f"   ✅ SUCCESS with database in path!")
        print(f"   Database: {db.name}")
        client.close()
        print(f"\n💡 SOLUTION: Update your .env file:")
        print(f"   MONGODB_HOST={new_conn}")
        sys.exit(0)
    except Exception as e:
        print(f"   ❌ Failed: {str(e)[:100]}")

# Format 3: URL-encode password (if it has special characters)
if has_creds_in_string:
    print(f"\n3️⃣ Testing: URL-encoding password")
    try:
        # Extract and re-encode
        if 'mongodb+srv://' in connection_string:
            parts = connection_string.replace('mongodb+srv://', '').split('@')
            if len(parts) == 2:
                creds = parts[0].split(':')
                if len(creds) == 2:
                    username = creds[0]
                    password = creds[1]
                    # URL encode password
                    encoded_password = quote_plus(password)
                    new_conn = f"mongodb+srv://{username}:{encoded_password}@{parts[1]}"
                    
                    # Add database if missing
                    if '/?' not in new_conn and not new_conn.split('@')[-1].split('/')[1:]:
                        new_conn = new_conn.rstrip('/') + f"/{mongodb_config['name']}?retryWrites=true&w=majority"
                    elif '/?' in new_conn:
                        new_conn = new_conn.replace('/?', f"/{mongodb_config['name']}?")
                    
                    client = MongoClient(new_conn, serverSelectionTimeoutMS=10000)
                    client.admin.command('ping')
                    db = client[mongodb_config['name']]
                    print(f"   ✅ SUCCESS with URL-encoded password!")
                    print(f"   Database: {db.name}")
                    client.close()
                    print(f"\n💡 SOLUTION: Update your .env file:")
                    print(f"   MONGODB_HOST={new_conn}")
                    sys.exit(0)
    except Exception as e:
        print(f"   ❌ Failed: {str(e)[:100]}")

print(f"\n❌ All connection attempts failed")
print(f"\n💡 Manual Fix Steps:")
print(f"   1. Go to MongoDB Atlas → Database → Connect")
print(f"   2. Choose 'Connect your application'")
print(f"   3. Copy the connection string")
print(f"   4. Replace <password> with your actual password")
print(f"   5. Add your database name: ...mongodb.net/mamacare_db?...")
print(f"   6. Update MONGODB_HOST in .env file")
print(f"\n   Example format:")
print(f"   MONGODB_HOST=mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@YOUR_CLUSTER.mongodb.net/mamacare_db?retryWrites=true&w=majority")
print(f"\n   Also verify:")
print(f"   - Username/password are correct in Atlas")
print(f"   - Your IP address is whitelisted in Atlas Network Access")
print(f"   - Database user has read/write permissions")

print("=" * 70)

