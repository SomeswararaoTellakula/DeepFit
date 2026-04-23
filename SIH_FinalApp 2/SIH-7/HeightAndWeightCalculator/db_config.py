from pymongo import MongoClient
import time

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
                if doc.get(k) != v: match = False; break
            if match: return doc
        return None
    def create_index(self, *args, **kwargs): pass

class MockDB:
    def __init__(self):
        self.users = MockCollection('users')
        self.height_videos = MockCollection('height_videos')
        self.exercise_sessions = MockCollection('exercise_sessions')
        self.exercise_results = MockCollection('exercise_results')
    def __getitem__(self, name):
        return getattr(self, name, MockCollection(name))

def connect_mongodb(max_retries=1, retry_delay=1):
    """
    Establish MongoDB connection with retry logic
    """
    try:
        client = MongoClient('mongodb://localhost:27017/',
                           serverSelectionTimeoutMS=2000,
                           connectTimeoutMS=2000)
        client.server_info()
        db = client['sih2573']
        # Ensure collections
        _ = db['users']
        return client, db
    except Exception as e:
        print(f"⚠️ MongoDB connection failed, using Mock DB: {e}")
        return None, MockDB()

def get_db():
    client, db = connect_mongodb()
    return db