from flask import Flask, request, jsonify
import uuid
import time
import base64
import json
from threading import Lock

app = Flask(__name__)

# Thread-safe storage for job status tracking
jobs = {}
job_poll_counts = {}
jobs_lock = Lock()

def generate_mock_base64_image():
    """Generate a mock base64 encoded image (1x1 pixel PNG)"""
    # Minimal 1x1 pixel PNG in base64
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

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
    
    # Validate input exists
    if 'input' not in data:
        return jsonify({"error": "Missing input field"}), 400
    
    input_data = data['input']
    
    # Generate a random UUID for the job
    job_id = str(uuid.uuid4()) + "-u1"
    
    # Log the received input data
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] New job {job_id}")
    print(f"Input received: {json.dumps(input_data, indent=2)}")
    
    # Check if this job should fail
    should_fail = False
    fail_message = "Processing failed"
    if isinstance(input_data, dict) and 'fail' in input_data:
        should_fail = True
        if isinstance(input_data['fail'], str) and input_data['fail']:
            fail_message = input_data['fail']
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Job {job_id} marked to fail: {fail_message}")
    
    # Store job data
    with jobs_lock:
        jobs[job_id] = {
            "id": job_id,
            "status": "IN_PROGRESS",
            "created_at": time.time(),
            "input": input_data,
            "should_fail": should_fail,
            "fail_message": fail_message
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
        
        # Log status check
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Status check for {job_id} (poll #{poll_count})")
        
        # First 3 polls return IN_PROGRESS
        if poll_count <= 3:
            return jsonify({
                "id": job_id,
                "status": "IN_PROGRESS"
            })
        else:
            # 4th and subsequent polls return COMPLETED or FAILED
            if job.get("should_fail", False):
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Job {job_id} failed: {job['fail_message']}")
                return jsonify({
                    "id": job_id,
                    "status": "FAILED",
                    "output": {
                        "error": job["fail_message"]
                    }
                })
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Job {job_id} completed")
                return jsonify({
                    "id": job_id,
                    "status": "COMPLETED",
                    "output": {
                        "image": generate_mock_base64_image()
                    }
                })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    print("Starting Mock Python Server on http://0.0.0.0:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False) 