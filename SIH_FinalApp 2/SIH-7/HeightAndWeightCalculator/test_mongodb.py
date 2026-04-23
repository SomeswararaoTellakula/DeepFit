from pymongo import MongoClient
from datetime import datetime

# Test MongoDB connection
try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ MongoDB connection successful")
    
    # Access database and collection
    db = client['USER']
    collection = db['Vertical_Jump']
    
    # Test data
    test_data = {
        'session_start': datetime.now().isoformat(),
        'total_jumps': 1,
        'max_height': 25.5,
        'test': True,
        'jumps': [
            {
                'timestamp': datetime.now().isoformat(),
                'height_cm': 25.5,
                'jump_number': 1
            }
        ]
    }
    
    # Insert test data
    result = collection.insert_one(test_data)
    print(f"✅ Test data inserted: {result.inserted_id}")
    print(f"Database: {db.name}")
    print(f"Collection: {collection.name}")
    
    # Verify insertion
    count = collection.count_documents({})
    print(f"Total documents in collection: {count}")
    
except Exception as e:
    print(f"❌ Error: {e}")