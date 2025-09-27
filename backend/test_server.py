"""Simple test server to verify basic functionality."""

import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Test Server")

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Test server is running"}

@app.get("/")
def root():
    return {"message": "Test server root endpoint"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)