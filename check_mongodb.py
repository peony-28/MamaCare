"""
Quick script to test MongoDB connection
Run this to diagnose database connection issues
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mamacare_project.settings')
django.setup()

from django.conf import settings
from pymongo import MongoClient

print("=" * 60)
print("MongoDB Connection Test")
print("=" * 60)

mongodb_config = settings.MONGODB_SETTINGS
print(f"\n📋 Configuration:")
print(f"   Host: {mongodb_config['host']}")
print(f"   Database: {mongodb_config['name']}")
print(f"   Username: {'***' if mongodb_config.get('username') else '(not set)'}")
print(f"   Password: {'***' if mongodb_config.get('password') else '(not set)'}")

connection_string = mongodb_config['host']

# Build connection string with credentials if provided
if mongodb_config.get('username') and mongodb_config.get('password'):
    if '@' not in connection_string:
        if connection_string.startswith('mongodb://'):
            connection_string = connection_string.replace(
                'mongodb://',
                f"mongodb://{mongodb_config['username']}:{mongodb_config['password']}@"
            )
        elif connection_string.startswith('mongodb+srv://'):
            connection_string = connection_string.replace(
                'mongodb+srv://',
                f"mongodb+srv://{mongodb_config['username']}:{mongodb_config['password']}@"
            )

print(f"\n🔌 Attempting connection...")
print(f"   Connection string: {connection_string.split('@')[-1] if '@' in connection_string else connection_string}")

try:
    client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
    # Test connection
    client.admin.command('ping')
    db = client[mongodb_config['name']]
    
    print(f"\n✅ SUCCESS! Connected to MongoDB")
    print(f"   Database: {db.name}")
    print(f"   Server version: {client.server_info().get('version', 'unknown')}")
    
    # Test write
    test_collection = db['test_connection']
    test_doc = {'test': True, 'timestamp': 'now'}
    result = test_collection.insert_one(test_doc)
    test_collection.delete_one({'_id': result.inserted_id})
    print(f"   ✅ Write test: PASSED")
    
    # Check if predictions collection exists
    collections = db.list_collection_names()
    if 'predictions' in collections:
        count = db.predictions.count_documents({})
        print(f"   📊 Existing predictions: {count}")
    else:
        print(f"   📊 Predictions collection: Will be created on first save")
    
    client.close()
    print(f"\n✅ All tests passed! MongoDB is ready to use.")
    
except Exception as e:
    print(f"\n❌ CONNECTION FAILED")
    print(f"   Error: {str(e)}")
    print(f"\n💡 Troubleshooting:")
    print(f"   1. Check your .env file has correct MONGODB_HOST")
    print(f"   2. For MongoDB Atlas: Ensure your IP is whitelisted")
    print(f"   3. For local MongoDB: Ensure MongoDB is running")
    print(f"   4. Check username/password are correct")
    print(f"\n   Note: Predictions will still work without MongoDB,")
    print(f"   but they won't be saved to the database.")
    sys.exit(1)

print("=" * 60)

