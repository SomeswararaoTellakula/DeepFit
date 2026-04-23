from flask import Blueprint, jsonify, session, request
from dynamic_benchmarks import DynamicBenchmarkSystem
from datetime import datetime
import logging

# Create blueprint for benchmark routes
benchmark_bp = Blueprint('benchmarks', __name__)

# Initialize the benchmark system
try:
    benchmark_system = DynamicBenchmarkSystem()
    print("[OK] Dynamic benchmark system initialized successfully")
except Exception as e:
    print(f"[ERROR] Error initializing benchmark system: {e}")
    benchmark_system = None

@benchmark_bp.route('/api/match_athlete', methods=['POST'])
def match_athlete():
    """API endpoint to match athlete based on user profile data"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No user data provided"
            }), 400
        
        # Validate required fields
        required_fields = ['age', 'gender', 'height', 'weight']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        if not benchmark_system:
            return jsonify({
                "success": False,
                "error": "Benchmark system not initialized"
            }), 500
        
        # Find closest matching athlete
        matched_athlete = benchmark_system.find_closest_athlete(
            float(data['height']),
            float(data['weight']),
            int(data['age']),
            data['gender']
        )
        
        if matched_athlete is None:
            return jsonify({
                "success": False,
                "error": "No matching athlete found"
            }), 404
        
        return jsonify({
            "success": True,
            "benchmarks": {
                "situp": float(matched_athlete['Situps_per_min']),
                "vertical_jump": float(matched_athlete['Vertical_Jump_cm']),
                "dumbbell": float(matched_athlete['Dumbbell_Curl_per_min'])
            },
            "matched_athlete_id": int(matched_athlete['Athlete_ID']),
            "user_profile": data,
            "athlete_profile": {
                "height": float(matched_athlete['Height_cm']),
                "weight": float(matched_athlete['Weight_kg']),
                "age": int(matched_athlete['Age']),
                "gender": matched_athlete['Gender']
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error in match_athlete: {e}")
        return jsonify({
            "success": False,
            "error": f"System error: {str(e)}"
        }), 500

@benchmark_bp.route('/api/benchmark_info')
def get_benchmark_info():
    """Get information about the benchmark matching system"""
    try:
        user_email = session.get('user_email')
        
        if not user_email or not benchmark_system:
            return jsonify({
                "success": False,
                "message": "Benchmark system not available"
            })
        
        benchmarks = benchmark_system.get_dynamic_benchmarks(user_email)
        
        return jsonify({
            "success": True,
            "info": {
                "total_athletes": len(benchmark_system.athlete_df),
                "matched_athlete": benchmarks.get("matched_athlete_id"),
                "user_profile": benchmarks.get("user_profile"),
                "athlete_profile": benchmarks.get("athlete_profile"),
                "matching_algorithm": "Nearest-neighbor based on height, weight, age, and gender"
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500