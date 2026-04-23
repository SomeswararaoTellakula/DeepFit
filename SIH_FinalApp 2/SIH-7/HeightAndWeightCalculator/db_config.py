from pymongo import MongoClient
import time
import os

# Singleton instance for Mock DB to persist data during the app's runtime
_mock_db_instance = None

class MockCollection:
    def __init__(self, name):
        self.name = name
        self.data = {}
    def insert_one(self, doc):
        from bson import ObjectId
        if '_id' not in doc: doc['_id'] = ObjectId()
        self.data[str(doc['_id'])] = doc
        return type('obj', (object,), {'inserted_id': doc['_id']})
    def find_one(self, query, sort=None):
        for doc in self.data.values():
            match = True
            for k, v in query.items():
                # Handle ObjectId comparison
                if str(doc.get(k)) != str(v): match = False; break
            if match: return doc
        return None
    def find(self, query=None):
        return list(self.data.values())
    def create_index(self, *args, **kwargs): pass

class MockDB:
    def __init__(self):
        self.users = MockCollection('users')
        self.height_videos = MockCollection('height_videos')
        self.exercise_sessions = MockCollection('exercise_sessions')
        self.exercise_results = MockCollection('exercise_results')
    def __getitem__(self, name):
        if not hasattr(self, name):
            setattr(self, name, MockCollection(name))
        return getattr(self, name)

def connect_mongodb():
    global _mock_db_instance
    
    # Check for MONGODB_URI in environment variables (for Atlas/Production)
    uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    
    try:
        client = MongoClient(uri,
                           serverSelectionTimeoutMS=2000,
                           connectTimeoutMS=2000)
        client.server_info()
        db = client['sih2573']
        return client, db
    except Exception as e:
        if _mock_db_instance is None:
            print(f"ℹ️ Local MongoDB not found. Initializing Persistent Mock DB for this session.")
            _mock_db_instance = MockDB()
        return None, _mock_db_instance

def get_db():
    _, db = connect_mongodb()
    return db