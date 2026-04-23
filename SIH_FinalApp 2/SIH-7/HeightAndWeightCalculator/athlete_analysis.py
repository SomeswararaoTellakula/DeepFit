import pandas as pd
import numpy as np
from datetime import datetime

def analyze_athlete_dataset():
    """Comprehensive analysis of AthleteData.csv"""
    
    # Load the dataset
    df = pd.read_csv('AthleteData.csv')
    
    print("=== ATHLETE DATASET ANALYSIS ===\n")
    
    # 1. Dataset Structure
    print("1. DATASET STRUCTURE:")
    print(f"   - Total Records: {len(df)}")
    print(f"   - Columns: {list(df.columns)}")
    print(f"   - Data Types:\n{df.dtypes}")
    print()
    
    # 2. Missing Values Check
    print("2. DATA QUALITY:")
    missing_values = df.isnull().sum()
    print(f"   - Missing Values:\n{missing_values}")
    print(f"   - Complete Records: {len(df.dropna())}")
    print()
    
    # 3. Performance Metrics Analysis
    print("3. PERFORMANCE METRICS AVAILABILITY:")
    performance_cols = ['Situps_per_min', 'Vertical_Jump_cm', 'Dumbbell_Curl_per_min']
    for col in performance_cols:
        print(f"   - {col}: Range [{df[col].min():.1f} - {df[col].max():.1f}], Mean: {df[col].mean():.1f}")
    print()
    
    # 4. Demographic Distribution
    print("4. DEMOGRAPHIC DISTRIBUTION:")
    print(f"   - Age: Range [{df['Age'].min()} - {df['Age'].max()}], Mean: {df['Age'].mean():.1f}")
    print(f"   - Height (cm): Range [{df['Height_cm'].min():.1f} - {df['Height_cm'].max():.1f}], Mean: {df['Height_cm'].mean():.1f}")
    print(f"   - Weight (kg): Range [{df['Weight_kg'].min():.1f} - {df['Weight_kg'].max():.1f}], Mean: {df['Weight_kg'].mean():.1f}")
    print(f"   - Gender Distribution:\n{df['Gender'].value_counts()}")
    print()
    
    # 5. Data Validation
    print("5. DATA VALIDATION:")
    # Check for reasonable ranges
    valid_height = df[(df['Height_cm'] >= 140) & (df['Height_cm'] <= 220)]
    valid_weight = df[(df['Weight_kg'] >= 40) & (df['Weight_kg'] <= 150)]
    valid_age = df[(df['Age'] >= 15) & (df['Age'] <= 40)]
    
    print(f"   - Valid Height Records: {len(valid_height)}/{len(df)} ({len(valid_height)/len(df)*100:.1f}%)")
    print(f"   - Valid Weight Records: {len(valid_weight)}/{len(df)} ({len(valid_weight)/len(df)*100:.1f}%)")
    print(f"   - Valid Age Records: {len(valid_age)}/{len(df)} ({len(valid_age)/len(df)*100:.1f}%)")
    print()
    
    return df

def find_closest_athlete(user_height, user_weight, user_age, user_gender, df):
    """Find the closest matching athlete using nearest-neighbor algorithm"""
    
    GENDER_PENALTY = 50  # Large penalty for gender mismatch
    
    best_score = float('inf')
    best_athlete = None
    
    for _, athlete in df.iterrows():
        # Calculate similarity score
        height_diff = abs(athlete['Height_cm'] - user_height)
        weight_diff = abs(athlete['Weight_kg'] - user_weight)
        age_diff = abs(athlete['Age'] - user_age)
        gender_penalty = GENDER_PENALTY if athlete['Gender'] != user_gender else 0
        
        total_score = height_diff + weight_diff + age_diff + gender_penalty
        
        if total_score < best_score:
            best_score = total_score
            best_athlete = athlete
    
    return best_athlete, best_score

def test_matching_algorithm():
    """Test the matching algorithm with sample users"""
    
    df = pd.read_csv('AthleteData.csv')
    
    print("=== TESTING MATCHING ALGORITHM ===\n")
    
    # Test cases
    test_users = [
        {"height": 175, "weight": 70, "age": 25, "gender": "M"},
        {"height": 165, "weight": 60, "age": 22, "gender": "F"},
        {"height": 180, "weight": 80, "age": 30, "gender": "M"}
    ]
    
    for i, user in enumerate(test_users, 1):
        print(f"Test User {i}: {user}")
        
        matched_athlete, score = find_closest_athlete(
            user["height"], user["weight"], user["age"], user["gender"], df
        )
        
        print(f"Matched Athlete: ID {matched_athlete['Athlete_ID']}")
        print(f"  - Height: {matched_athlete['Height_cm']}cm (diff: {abs(matched_athlete['Height_cm'] - user['height']):.1f})")
        print(f"  - Weight: {matched_athlete['Weight_kg']}kg (diff: {abs(matched_athlete['Weight_kg'] - user['weight']):.1f})")
        print(f"  - Age: {matched_athlete['Age']} (diff: {abs(matched_athlete['Age'] - user['age'])})")
        print(f"  - Gender: {matched_athlete['Gender']} (match: {matched_athlete['Gender'] == user['gender']})")
        print(f"  - Total Score: {score:.1f}")
        print(f"Benchmarks:")
        print(f"  - Situps: {matched_athlete['Situps_per_min']}")
        print(f"  - Vertical Jump: {matched_athlete['Vertical_Jump_cm']}")
        print(f"  - Dumbbell Curl: {matched_athlete['Dumbbell_Curl_per_min']}")
        print()

if __name__ == "__main__":
    # Run analysis
    df = analyze_athlete_dataset()
    
    # Test matching
    test_matching_algorithm()