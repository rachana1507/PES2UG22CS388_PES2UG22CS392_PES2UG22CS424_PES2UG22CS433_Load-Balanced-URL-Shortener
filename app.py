from flask import Flask, request, redirect, jsonify
import redis
import random
import string
import os
import socket


# Initialize Flask app
app = Flask(__name__)

# Redis connection using environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "redis-server")  # Use "redis-server" for Docker networking
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Connect to Redis
db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_timeout=5)

def generate_short_code():
    """Generates a unique 6-character short code."""
    while True:
        short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        if not db.exists(short_code):  # Ensure uniqueness
            return short_code

#@app.route('/')
#def home():
#    """Root endpoint to check if the API is running."""
#    return jsonify({"message": "URL Shortener API is running!"})

@app.route('/')
def home():
    """Root endpoint with hostname"""
    hostname = socket.gethostname()
    return jsonify({
        "message": "URL Shortener API is running!",
        "hostname": hostname  # ← Add this line
    })

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """Accepts a long URL, generates a short URL, and stores it in Redis."""
    data = request.get_json()
    long_url = data.get("url")

    if not long_url:
        return jsonify({"error": "URL is required"}), 400

    short_code = generate_short_code()
    db.set(short_code, long_url)
    
    base_url = request.host_url  # Gets http://<service-ip>:<port>/
    return jsonify({"short_url": f"{base_url}{short_code}"})
  
@app.route('/<short_code>')
def redirect_url(short_code):
    try:
        long_url = db.get(short_code)
        if long_url:
            return redirect(long_url)  # Remove .decode('utf-8')
        return jsonify({"error": "URL not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


"""  
    
@app.route('/<short_code>')
def redirect_url(short_code):
    try:
        long_url = db.get(short_code)
        if long_url:
            return redirect(long_url.decode('utf-8'))  # Critical: decode Redis bytes
        return jsonify({"error": "URL not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


