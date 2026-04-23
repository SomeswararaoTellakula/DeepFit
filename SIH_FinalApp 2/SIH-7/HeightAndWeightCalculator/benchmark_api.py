
from flask import Flask, jsonify, request, session
from dynamic_benchmarks import DynamicBenchmarkSystem

app = Flask(__name__)
benchmark_system = DynamicBenchmarkSystem()

@app.route('/api/dynamic_benchmarks')
def get_dynamic_benchmarks():
    """API endpoint to get dynamic benchmarks for current user"""
    try:
        # Get user email from session or request
        user_email = session.get('user_email') or request.args.get('user_email')
        
        if not user_email:
            return jsonify({
                "error": "User not authenticated",
                "benchmarks": {"situp": 6, "vertical_jump": 4, "dumbbell": 7}
            }), 400
        
        # Get dynamic benchmarks
        benchmarks = benchmark_system.get_dynamic_benchmarks(user_email)
        
        return jsonify({
            "success": True,
            "benchmarks": benchmarks,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "benchmarks": {"situp": 6, "vertical_jump": 4, "dumbbell": 7}
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
