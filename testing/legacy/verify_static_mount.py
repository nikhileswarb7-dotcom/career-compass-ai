import sys
import os
import time
import requests
import threading
import uvicorn

# Add workspace root to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from api.app import app

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")

if __name__ == "__main__":
    # Start server in a background thread
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Try different paths
    for path in ["/frontend", "/frontend/", "/frontend/index.html"]:
        url = f"http://127.0.0.1:8001{path}"
        try:
            r = requests.get(url)
            print(f"GET {path} -> Status {r.status_code}")
            if r.status_code == 200:
                print("Content sample:\n", r.text[:200])
                print("-" * 50)
        except Exception as e:
            print(f"GET {path} -> ERROR: {e}")
