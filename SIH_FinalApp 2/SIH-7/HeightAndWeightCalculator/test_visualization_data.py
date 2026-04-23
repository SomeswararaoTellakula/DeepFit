#!/usr/bin/env python3
"""
Test script to verify MongoDB data structure and create sample data for visualizations
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import random

def test_mongodb_connection():
    """Test MongoDB connection and collections"""
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["sih2573"]
        
        print("✅ MongoDB connection successful")
        print(f"📊 Available collections: {db.list_collection_names()}")
        
        return client, db
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return None, None

def create_sample_situp_data(db):
    """Create sample situp data for testing"""
    situps_collection = db['situps']
    
    # Create 10 sample records
    sample_data = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(10):
        date = base_date + timedelta(days=i*3)
        sample_data.append({
            'user_email': 'test@example.com',
            'reps_completed': random.randint(15, 35),
            'form_quality': random.randint(70, 95),
            'timer_time': f"{random.randint(1, 3)}:{random.randint(10, 59):02d}",
            'submission_time': date,
            'created_at': date
        })
    
    try:
        result = situps_collection.insert_many(sample_data)
        print(f"✅ Created {len(result.inserted_ids)} sample situp records")
    except Exception as e:
        print(f"❌ Error creating situp data: {e}")

def create_sample_dumbbell_data(db):
    """Create sample dumbbell data for testing"""
    dumbbell_collection = db['DumbBell']
    
    # Create 10 sample records
    sample_data = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(10):
        date = base_date + timedelta(days=i*3)
        left_reps = random.randint(8, 15)
        right_reps = random.randint(8, 15)
        
        sample_data.append({
            'timestamp': date.strftime('%Y%m%d_%H%M%S'),
            'exercise_type': 'dumbbell_curls',
            'estimated_weight': round(random.uniform(5.0, 25.0), 2),
            'left_reps': left_reps,
            'right_reps': right_reps,
            'total_reps': left_reps + right_reps,
            'left_tempos': [random.uniform(1.0, 3.0) for _ in range(left_reps)],
            'right_tempos': [random.uniform(1.0, 3.0) for _ in range(right_reps)],
            'left_roms': [random.uniform(120, 170) for _ in range(left_reps)],
            'right_roms': [random.uniform(120, 170) for _ in range(right_reps)],
            'session_duration': round(random.uniform(60, 180), 2),
            'analysis_date': date.isoformat()
        })
    
    try:
        result = dumbbell_collection.insert_many(sample_data)
        print(f"✅ Created {len(result.inserted_ids)} sample dumbbell records")
    except Exception as e:
        print(f"❌ Error creating dumbbell data: {e}")

def create_sample_vertical_jump_data(db):
    """Create sample vertical jump data for testing"""
    jump_collection = db['VerticalJump']
    
    # Create 5 sample sessions
    sample_data = []
    base_date = datetime.now() - timedelta(days=20)
    
    for i in range(5):
        session_date = base_date + timedelta(days=i*4)
        num_jumps = random.randint(3, 8)
        
        # Generate individual jumps
        jumps = []
        heights = []
        for j in range(num_jumps):
            height = random.uniform(45, 75)
            heights.append(height)
            jumps.append({
                'timestamp': (session_date + timedelta(seconds=j*10)).isoformat(),
                'height_cm': height,
                'jump_number': j + 1,
                'body_angle': random.uniform(-2, 2),
                'knee_angles': {
                    'left': random.uniform(165, 180),
                    'right': random.uniform(165, 180)
                },
                'confidence': random.uniform(0.85, 0.99),
                'pixels_per_cm': random.uniform(1.8, 2.0)
            })
        
        sample_data.append({
            'session_start': session_date.isoformat(),
            'total_jumps': num_jumps,
            'max_height': max(heights),
            'average_height': sum(heights) / len(heights),
            'calibration_data': {
                'pixels_per_cm': random.uniform(1.8, 2.0),
                'baseline_y': random.uniform(650, 700)
            },
            'jumps': jumps
        })
    
    try:
        result = jump_collection.insert_many(sample_data)
        print(f"✅ Created {len(result.inserted_ids)} sample vertical jump records")
    except Exception as e:
        print(f"❌ Error creating vertical jump data: {e}")

def verify_data(db):
    """Verify the created data"""
    collections = ['situps', 'DumbBell', 'VerticalJump']
    
    for collection_name in collections:
        try:
            collection = db[collection_name]
            count = collection.count_documents({})
            print(f"📊 {collection_name}: {count} documents")
            
            # Show sample document
            sample = collection.find_one()
            if sample:
                print(f"   Sample fields: {list(sample.keys())}")
        except Exception as e:
            print(f"❌ Error checking {collection_name}: {e}")

def main():
    print("🚀 Testing MongoDB Visualization Data Setup")
    print("=" * 50)
    
    client, db = test_mongodb_connection()
    if not db:
        return
    
    print("\n📝 Creating sample data...")
    create_sample_situp_data(db)
    create_sample_dumbbell_data(db)
    create_sample_vertical_jump_data(db)
    
    print("\n🔍 Verifying data...")
    verify_data(db)
    
    print("\n✅ Setup complete! You can now test the visualization pages:")
    print("   - http://localhost:5000/displaysitup")
    print("   - http://localhost:5000/displaydumbbell") 
    print("   - http://localhost:5000/displayVerticalJump")

if __name__ == "__main__":
    main()