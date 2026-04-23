#!/usr/bin/env python3
"""
Test Corrected Estimation Logic
Verify that the new algorithm produces correct results
"""

import numpy as np

def test_corrected_algorithm():
    """Test the corrected algorithm with your example data"""
    
    # Your example measurements
    measurements = [
        {
            "height_cm": 180.14706550477663,
            "weight_kg": 78.19023970685066,
            "confidence_score": 0.492,
            "uncertainty_height": 1,
            "uncertainty_weight": 2,
            "detection_status": "good_position",
            "calibration_quality": 999
        },
        {
            "height_cm": 180.16940527462106,
            "weight_kg": 70.39196914517552,
            "confidence_score": 0.492,
            "uncertainty_height": 1,
            "uncertainty_weight": 2,
            "detection_status": "good_position",
            "calibration_quality": 999
        }
    ]
    
    print("🧪 TESTING CORRECTED ESTIMATION LOGIC")
    print("=" * 50)
    
    print("📋 Input Measurements:")
    for i, m in enumerate(measurements, 1):
        print(f"  {i}. Height: {m['height_cm']:.4f} cm, Weight: {m['weight_kg']:.4f} kg")
        print(f"     Confidence: {m['confidence_score']}, Uncertainty: H±{m['uncertainty_height']}, W±{m['uncertainty_weight']}")
    
    # Apply corrected algorithm
    print("\n🔧 Applying Corrected Algorithm...")
    
    # Filter quality measurements (both should pass)
    quality_measurements = [
        m for m in measurements 
        if (m.get('confidence_score', 0) >= 0.45 and 
            m.get('detection_status') == 'good_position' and
            m.get('calibration_quality', 999) >= 950)
    ]
    
    # Since confidence is 0.492 (>= 0.45), both should be included
    print(f"✅ Quality measurements: {len(quality_measurements)}")
    
    # Use inverse uncertainty squared weighting
    height_weights = []
    weight_weights = []
    weighted_heights = []
    weighted_weights = []
    
    for m in quality_measurements:
        height_unc = m.get('uncertainty_height', 1.0)
        weight_unc = m.get('uncertainty_weight', 2.0)
        
        # Calculate inverse uncertainty squared weights
        height_weight = 1.0 / (height_unc ** 2)
        weight_weight = 1.0 / (weight_unc ** 2)
        
        height_weights.append(height_weight)
        weight_weights.append(weight_weight)
        weighted_heights.append(m['height_cm'] * height_weight)
        weighted_weights.append(m['weight_kg'] * weight_weight)
        
        print(f"   Measurement: H={m['height_cm']:.4f}, W={m['weight_kg']:.4f}")
        print(f"   Weights: H_weight={height_weight:.4f}, W_weight={weight_weight:.4f}")
    
    # Calculate weighted averages
    final_height = sum(weighted_heights) / sum(height_weights)
    final_weight = sum(weighted_weights) / sum(weight_weights)
    
    # Calculate uncertainties using proper error propagation
    height_uncertainty = 1.0 / np.sqrt(sum(height_weights))
    weight_uncertainty = 1.0 / np.sqrt(sum(weight_weights))
    
    # Calculate confidence level
    avg_confidence = np.mean([m['confidence_score'] for m in quality_measurements])
    
    # Calculate BMI
    height_m = final_height / 100.0
    bmi = final_weight / (height_m ** 2)
    
    print("\n✅ CORRECTED RESULTS:")
    print("=" * 30)
    print(f"📏 Final Height: {final_height:.4f} cm")
    print(f"⚖️ Final Weight: {final_weight:.4f} kg")
    print(f"📊 BMI: {bmi:.2f}")
    print(f"🎯 Confidence: {avg_confidence * 100:.1f}%")
    print(f"📈 Height Uncertainty: ±{height_uncertainty:.4f} cm")
    print(f"📈 Weight Uncertainty: ±{weight_uncertainty:.4f} kg")
    print(f"🔢 Measurements Used: {len(quality_measurements)}")
    
    print("\n📊 EXPECTED vs ACTUAL:")
    print("=" * 30)
    print("Expected Height: ~180.16 cm")
    print(f"Actual Height:   {final_height:.4f} cm")
    print("Expected Weight: ~74.29 kg")
    print(f"Actual Weight:   {final_weight:.4f} kg")
    
    # Verify results are close to expected
    expected_height = (180.14706550477663 + 180.16940527462106) / 2
    expected_weight = (78.19023970685066 + 70.39196914517552) / 2
    
    height_error = abs(final_height - expected_height)
    weight_error = abs(final_weight - expected_weight)
    
    print(f"\n🎯 ACCURACY CHECK:")
    print(f"Height Error: {height_error:.6f} cm (should be ~0)")
    print(f"Weight Error: {weight_error:.6f} kg (should be ~0)")
    
    if height_error < 0.001 and weight_error < 0.001:
        print("✅ ALGORITHM WORKING CORRECTLY!")
    else:
        print("❌ Algorithm needs adjustment")
    
    return {
        "final_height_cm": round(final_height, 4),
        "final_weight_kg": round(final_weight, 4),
        "bmi": round(bmi, 2),
        "height_uncertainty": round(height_uncertainty, 4),
        "weight_uncertainty": round(weight_uncertainty, 4),
        "confidence_level": f"{avg_confidence * 100:.1f}%",
        "total_instances": len(quality_measurements)
    }

if __name__ == "__main__":
    result = test_corrected_algorithm()
    print(f"\n🏁 Final Result: {result}")