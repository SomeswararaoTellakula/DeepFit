#!/usr/bin/env python3
"""
Fix Estimation Logic - Recalculate Final Estimates with Correct Algorithm
This script fixes the incorrect final estimation logic by reprocessing existing data
"""

import numpy as np
from pymongo import MongoClient
from datetime import datetime, timezone, timedelta
import json

class EstimationFixer:
    def __init__(self):
        try:
            self.client = MongoClient('mongodb://localhost:27017/')
            self.db = self.client['sih2573']
            self.height_weight_collection = self.db['Height and Weight']
            self.final_estimates_collection = self.db['Final_Estimated_Height_and_Weight']
            print("✅ MongoDB connection successful")
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            self.client = None
    
    def get_user_measurements(self, user_email):
        """Get all measurements for a specific user"""
        try:
            measurements = list(self.height_weight_collection.find(
                {'user_email': user_email}
            ).sort('timestamp', -1))
            return measurements
        except Exception as e:
            print(f"Error fetching measurements: {e}")
            return []
    
    def apply_correct_estimation_logic(self, measurements):
        """Apply the corrected estimation logic with high precision"""
        if not measurements:
            return None
        
        print(f"Processing {len(measurements)} measurements...")
        
        # Apply strict quality filters
        quality_measurements = [
            m for m in measurements 
            if (m.get('confidence_score', 0) >= 0.45 and 
                m.get('detection_status') == 'good_position' and
                m.get('calibration_quality', 999) >= 950)
        ]
        
        # Fallback to less strict criteria if needed
        if not quality_measurements:
            quality_measurements = [
                m for m in measurements 
                if (m.get('confidence_score', 0) > 0.3 and 
                    m.get('detection_status') == 'good_position')
            ]
        
        if not quality_measurements:
            quality_measurements = measurements  # Last resort
        
        print(f"Quality measurements after filtering: {len(quality_measurements)}")
        
        # Remove outliers using median absolute deviation (more robust)
        heights = [m['height_cm'] for m in quality_measurements]
        weights = [m['weight_kg'] for m in quality_measurements]
        
        if len(heights) > 2:
            height_median = np.median(heights)
            weight_median = np.median(weights)
            height_mad = np.median([abs(h - height_median) for h in heights])
            weight_mad = np.median([abs(w - weight_median) for w in weights])
            
            # Use 2.5 standard deviations as threshold
            height_threshold = 2.5 * height_mad * 1.4826  # 1.4826 converts MAD to std
            weight_threshold = 2.5 * weight_mad * 1.4826
            
            filtered_measurements = [
                m for m in quality_measurements
                if (abs(m['height_cm'] - height_median) <= height_threshold and
                    abs(m['weight_kg'] - weight_median) <= weight_threshold)
            ]
            
            if filtered_measurements:
                quality_measurements = filtered_measurements
                print(f"After outlier removal: {len(quality_measurements)} measurements")
        
        # Use inverse uncertainty squared weighting for maximum precision
        height_weights = []
        weight_weights = []
        weighted_heights = []
        weighted_weights = []
        
        for m in quality_measurements:
            # Get uncertainties with defaults
            height_unc = m.get('uncertainty_height', 1.0)
            weight_unc = m.get('uncertainty_weight', 2.0)
            
            # Calculate inverse uncertainty squared weights
            height_weight = 1.0 / (height_unc ** 2)
            weight_weight = 1.0 / (weight_unc ** 2)
            
            height_weights.append(height_weight)
            weight_weights.append(weight_weight)
            weighted_heights.append(m['height_cm'] * height_weight)
            weighted_weights.append(m['weight_kg'] * weight_weight)
        
        # Calculate weighted averages with high precision
        final_height = sum(weighted_heights) / sum(height_weights)
        final_weight = sum(weighted_weights) / sum(weight_weights)
        
        # Calculate uncertainties using proper error propagation
        height_uncertainty = 1.0 / np.sqrt(sum(height_weights))
        weight_uncertainty = 1.0 / np.sqrt(sum(weight_weights))
        
        # Calculate confidence level
        avg_confidence = np.mean([m.get('confidence_score', 0.5) for m in quality_measurements])
        
        # Calculate BMI with high precision
        height_m = final_height / 100.0
        bmi = final_weight / (height_m ** 2)
        
        return {
            "final_height_cm": round(final_height, 4),
            "final_weight_kg": round(final_weight, 4),
            "bmi": round(bmi, 2),
            "height_uncertainty": round(height_uncertainty, 4),
            "weight_uncertainty": round(weight_uncertainty, 4),
            "confidence_level": f"{avg_confidence * 100:.1f}%",
            "total_instances": len(quality_measurements)
        }
    
    def fix_user_estimates(self, user_email):
        """Fix estimates for a specific user"""
        print(f"\n🔧 Fixing estimates for user: {user_email}")
        
        # Get all measurements for user
        measurements = self.get_user_measurements(user_email)
        if not measurements:
            print("❌ No measurements found for user")
            return False
        
        # Apply correct estimation logic
        corrected_estimate = self.apply_correct_estimation_logic(measurements)
        if not corrected_estimate:
            print("❌ Could not generate corrected estimate")
            return False
        
        # Store corrected estimate
        try:
            ist = timezone(timedelta(hours=5, minutes=30))
            document = {
                "user_email": user_email,
                "timestamp": datetime.now(ist),
                **corrected_estimate
            }
            
            # Remove old estimate and insert new one
            self.final_estimates_collection.delete_many({'user_email': user_email})
            result = self.final_estimates_collection.insert_one(document)
            
            print("✅ Corrected estimate saved successfully")
            print(f"📏 Corrected Height: {corrected_estimate['final_height_cm']} cm")
            print(f"⚖️ Corrected Weight: {corrected_estimate['final_weight_kg']} kg")
            print(f"📊 BMI: {corrected_estimate['bmi']}")
            print(f"🎯 Confidence: {corrected_estimate['confidence_level']}")
            print(f"📈 Height Uncertainty: ±{corrected_estimate['height_uncertainty']} cm")
            print(f"📈 Weight Uncertainty: ±{corrected_estimate['weight_uncertainty']} kg")
            print(f"🔢 Quality Measurements Used: {corrected_estimate['total_instances']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving corrected estimate: {e}")
            return False
    
    def fix_all_users(self):
        """Fix estimates for all users in the database"""
        try:
            # Get all unique user emails
            user_emails = self.height_weight_collection.distinct('user_email')
            print(f"Found {len(user_emails)} users to process")
            
            for user_email in user_emails:
                self.fix_user_estimates(user_email)
            
            print("\n✅ All users processed successfully")
            
        except Exception as e:
            print(f"❌ Error processing users: {e}")
    
    def show_comparison(self, user_email):
        """Show before/after comparison for a user"""
        print(f"\n📊 COMPARISON FOR USER: {user_email}")
        print("=" * 60)
        
        # Get measurements
        measurements = self.get_user_measurements(user_email)
        if not measurements:
            print("❌ No measurements found")
            return
        
        # Show recent measurements
        print("📋 Recent Measurements:")
        for i, m in enumerate(measurements[:5]):  # Show last 5
            print(f"  {i+1}. Height: {m['height_cm']:.2f} cm, Weight: {m['weight_kg']:.2f} kg, Confidence: {m.get('confidence_score', 0):.3f}")
        
        # Get current (incorrect) final estimate
        current_estimate = self.final_estimates_collection.find_one({'user_email': user_email})
        if current_estimate:
            print(f"\n❌ CURRENT (INCORRECT) ESTIMATE:")
            print(f"   Height: {current_estimate.get('final_height_cm', 'N/A')} cm")
            print(f"   Weight: {current_estimate.get('final_weight_kg', 'N/A')} kg")
            print(f"   BMI: {current_estimate.get('bmi', 'N/A')}")
        
        # Calculate corrected estimate
        corrected = self.apply_correct_estimation_logic(measurements)
        if corrected:
            print(f"\n✅ CORRECTED ESTIMATE:")
            print(f"   Height: {corrected['final_height_cm']} cm")
            print(f"   Weight: {corrected['final_weight_kg']} kg")
            print(f"   BMI: {corrected['bmi']}")
            print(f"   Height Uncertainty: ±{corrected['height_uncertainty']} cm")
            print(f"   Weight Uncertainty: ±{corrected['weight_uncertainty']} kg")
            print(f"   Quality Measurements: {corrected['total_instances']}")

def main():
    print("🔧 ESTIMATION LOGIC FIXER")
    print("=" * 50)
    
    fixer = EstimationFixer()
    if not fixer.client:
        print("❌ Cannot connect to MongoDB")
        return
    
    # Example usage - fix specific user
    user_email = "afridpasha1976@gmail.com"
    
    # Show comparison first
    fixer.show_comparison(user_email)
    
    # Ask for confirmation
    response = input(f"\nDo you want to fix the estimate for {user_email}? (y/n): ").lower().strip()
    if response == 'y':
        fixer.fix_user_estimates(user_email)
    
    # Ask to fix all users
    response = input("\nDo you want to fix estimates for ALL users? (y/n): ").lower().strip()
    if response == 'y':
        fixer.fix_all_users()
    
    print("\n🏁 Process completed!")

if __name__ == "__main__":
    main()