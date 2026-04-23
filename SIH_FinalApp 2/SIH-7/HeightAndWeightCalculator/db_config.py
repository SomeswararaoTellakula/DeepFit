from pymongo import MongoClient
import time
import os
import json
from pymongo import MongoClient
import bcrypt
from bson import ObjectId

# Singleton instance for Mock DB
_mock_db_instance = None

class MockCollection:
    def __init__(self, name, db_file):
        self.name = name
        self.db_file = db_file
        self.data = self._load()
        
    def _load(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
        
    def _save(self):
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.data, f)
        except Exception as e:
            print(f"MockDB Save Error: {e}")

    def insert_one(self, doc):
        if '_id' not in doc: doc['_id'] = str(ObjectId())
        else: doc['_id'] = str(doc['_id'])
        self.data[doc['_id']] = doc
        self._save()
        return type('obj', (object,), {'inserted_id': doc['_id']})

    def find_one(self, query, sort=None):
        for doc in self.data.values():
            match = True
            for k, v in query.items():
                if str(doc.get(k)) != str(v): match = False; break
            if match: return doc
        return None

    def find(self, query=None):
        return list(self.data.values())

class MockDB:
    def __init__(self):
        db_dir = "mock_db_data"
        os.makedirs(db_dir, exist_ok=True)
        self.users = MockCollection('users', f"{db_dir}/users.json")
        self.height_videos = MockCollection('height_videos', f"{db_dir}/height.json")
        self.exercise_sessions = MockCollection('exercise_sessions', f"{db_dir}/sessions.json")
        self.exercise_results = MockCollection('exercise_results', f"{db_dir}/results.json")
        
        # Seed a demo account if users is empty
        if not self.users.find_one({'email': 'admin@deepfit.ai'}):
            hashed = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            self.users.insert_one({
                'email': 'admin@deepfit.ai',
                'password': hashed.decode('utf-8') if isinstance(hashed, bytes) else hashed,
                'name': 'Demo Admin',
                'age': 25,
                'gender': 'Other',
                'place': 'India'
            })

def connect_mongodb():
    global _mock_db_instance
    uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=1000)
        client.server_info()
        return client, client['sih2573']
    except:
        if _mock_db_instance is None:
            print("ℹ️ Using Persistent File-based Mock DB")
            _mock_db_instance = MockDB()
        return None, _mock_db_instance

def get_db():
    _, db = connect_mongodb()
    return db