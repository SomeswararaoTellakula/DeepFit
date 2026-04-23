from flask import Flask, request, jsonify
from dynamic_benchmarks import DynamicBenchmarkSystem

app = Flask(__name__)
benchmark_system = DynamicBenchmarkSystem()

@app.route('/api/match_athlete', methods=['POST'])
def match_athlete():
    data = request.json
    matched = benchmark_system.find_matching_athlete(data)
    if matched is None:
        return jsonify({'error': 'No matching athlete found'}), 404
    return jsonify(matched.to_dict())

@app.route('/api/dynamic_benchmarks')
def get_dynamic_benchmarks():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    benchmarks = benchmark_system.get_dynamic_benchmarks(email)
    return jsonify(benchmarks)

@app.route('/api/get_latest_measurement')
def get_latest_measurement():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    profile = benchmark_system.get_user_profile(email)
    return jsonify(profile) if profile else jsonify({'error': 'No data found'}), 404

@app.route('/api/test_benchmark_system')
def test_benchmark_system():
    test_profile = {'age': 25, 'gender': 'M', 'height': 175, 'weight': 70}
    matched = benchmark_system.find_matching_athlete(test_profile)
    
    if matched is None:
        return jsonify({'status': 'error', 'message': 'System test failed'})
    
    return jsonify({
        'status': 'success',
        'matched_athlete': matched.to_dict(),
        'benchmarks': {
            'situp': float(matched['Situps_per_min']),
            'vertical_jump': float(matched['Vertical_Jump_cm']),
            'dumbbell': float(matched['Dumbbell_Curl_per_min'])
        }
    })

if __name__ == '__main__':
    app.run(debug=True)