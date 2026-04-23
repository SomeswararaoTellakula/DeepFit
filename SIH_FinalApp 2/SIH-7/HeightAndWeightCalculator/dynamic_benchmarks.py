import pandas as pd
import numpy as np
from pymongo import MongoClient
from datetime import datetime

class DynamicBenchmarkSystem:
    def __init__(self, mongo_uri="mongodb://localhost:27017/", db_name="sih2573"):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.athlete_data = self.load_athlete_data()
        
    def load_athlete_data(self):
        try:
            return pd.read_csv('AthleteData.csv')
        except FileNotFoundError:
            print("AthleteData.csv not found")
            return None
    
    def get_user_profile(self, email):
        user = self.db.users.find_one({"email": email})
        if not user:
            return None
        
        # Get latest measurements from multiple collections
        height, weight = None, None
        collections = ['Height and Weight', 'Final_Estimated_Height_and_Weight', 'measurements']
        
        for collection_name in collections:
            if collection_name in self.db.list_collection_names():
                measurement = self.db[collection_name].find_one(
                    {"user_email": email}, 
                    sort=[("timestamp", -1)]
                )
                if measurement:
                    height = measurement.get('height_cm') or measurement.get('final_height_cm')
                    weight = measurement.get('weight_kg') or measurement.get('final_weight_kg')
                    if height and weight:
                        break
        
        return {
            'age': user.get('age'),
            'gender': user.get('gender'),
            'height': height,
            'weight': weight
        }
    
    def find_matching_athlete(self, user_profile):
        if self.athlete_data is None:
            raise ValueError("Athlete dataset not loaded")
        if not all(user_profile.values()):
            raise ValueError("Incomplete user profile data")
        
        scores = []
        for _, athlete in self.athlete_data.iterrows():
            score = (
                abs(athlete['Height_cm'] - user_profile['height']) +
                abs(athlete['Weight_kg'] - user_profile['weight']) +
                abs(athlete['Age'] - user_profile['age']) +
                (100 if athlete['Gender'] != user_profile['gender'] else 0)
            )
            scores.append(score)
        
        best_match_idx = np.argmin(scores)
        return self.athlete_data.iloc[best_match_idx]
    
    def get_dynamic_benchmarks(self, email):
        user_profile = self.get_user_profile(email)
        if not user_profile or not all(user_profile.values()):
            raise ValueError(f"Incomplete user profile for {email}")
        
        matched_athlete = self.find_matching_athlete(user_profile)
        if matched_athlete is None:
            raise ValueError(f"No matching athlete found for user {email}")
        
        return {
            'situp': float(matched_athlete['Situps_per_min']),
            'vertical_jump': float(matched_athlete['Vertical_Jump_cm']),
            'dumbbell': float(matched_athlete['Dumbbell_Curl_per_min'])
        }