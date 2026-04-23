import os
from pymongo import MongoClient

# Store global references to the connection so we don't spam reconnects
_mongo_client = None
_mongo_db = None

def connect_mongodb():
    global _mongo_client, _mongo_db
    
    # If already connected, return the existing connection
    if _mongo_client is not None and _mongo_db is not None:
        try:
            # Quick ping to ensure connection is still alive
            _mongo_client.admin.command('ping')
            return _mongo_client, _mongo_db
        except Exception:
            _mongo_client = None
            _mongo_db = None

    uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    
    try:
        print(f"🔗 Attempting to connect to MongoDB at: {uri.split('@')[-1] if '@' in uri else uri}")
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # This will raise an exception if the server is not reachable
        client.admin.command('ping')
        
        print("✅ Successfully connected to real MongoDB!")
        
        _mongo_client = client
        _mongo_db = client['sih2573']
        
        return _mongo_client, _mongo_db
    except Exception as e:
        print(f"❌ CRITICAL ERROR: Failed to connect to real MongoDB! Error: {e}")
        print("Please ensure your MONGODB_URI environment variable is set correctly in Hugging Face Settings -> Variables.")
        # We explicitly raise the error here because the user wants NO mock db.
        # The app should fail if there's no DB.
        raise RuntimeError(f"MongoDB Connection Required: {e}")

def get_db():
    _, db = connect_mongodb()
    return db