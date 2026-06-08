# FastAPI Application Entrypoint - CareerCompass AI

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load local .env file if it exists at the root of the workspace
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if os.path.exists(dotenv_path):
    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

from routes import router
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="CareerCompass AI API",
    description="API Backend for NLP-Based SDE Career Roadmaps",
    version="1.0"
)

# Mount the frontend directory to serve static UI pages
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

# Enable CORS for frontend pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for local testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "CareerCompass AI Backend",
        "message": "FastAPI is running successfully. Access endpoints via /api"
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
