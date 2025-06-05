from flask import Flask, request, jsonify
import uuid
import time
from threading import Lock

app = Flask(__name__)

# Thread-safe storage for job status tracking
jobs = {}
job_poll_counts = {}
jobs_lock = Lock()

@app.route('/run', methods=['POST'])
def run_job():
    # Check authentication
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthenticated"}), 401
    
    # Get the request data
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    
    # Validate input
    if 'input' not in data:
        return jsonify({"error": "Missing input field"}), 400
    
    input_data = data['input']
    
    # Check if input is an array of strings
    if not isinstance(input_data, list):
        return jsonify({"error": "input must be array of strings"}), 400
    
    for item in input_data:
        if not isinstance(item, str):
            return jsonify({"error": "input must be array of strings"}), 400
    
    # Generate a random UUID for the job
    job_id = str(uuid.uuid4()) + "-u1"
    
    # Store job data
    with jobs_lock:
        jobs[job_id] = {
            "id": job_id,
            "status": "IN_PROGRESS",
            "created_at": time.time(),
            "input": input_data
        }
        job_poll_counts[job_id] = 0
    
    return jsonify({
        "id": job_id,
        "status": "IN_PROGRESS"
    })

@app.route('/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    with jobs_lock:
        if job_id not in jobs:
            return jsonify({"error": "Job not found"}), 404
        
        # Increment poll count
        job_poll_counts[job_id] += 1
        poll_count = job_poll_counts[job_id]
        
        job = jobs[job_id]
        
        # First 3 polls return IN_PROGRESS
        if poll_count <= 3:
            return jsonify({
                "id": job_id,
                "status": "IN_PROGRESS"
            })
        else:
            # 4th and subsequent polls return COMPLETED
            return jsonify({
                "id": job_id,
                "status": "COMPLETED",
                "output": {
                    "uuid": str(uuid.uuid4())
                }
            })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 