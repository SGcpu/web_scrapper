"""Test API with CORS headers."""

import argparse
import sys
import time
import requests
from urllib.parse import urljoin

def test_api_with_cors(base_url, origin):
    """Test the API with CORS headers."""
    headers = {"Origin": origin}
    try:
        resp = requests.get(urljoin(base_url, "/health"), headers=headers)
        print(f"Status Code: {resp.status_code}")
        print(f"Response: {resp.text}")
        print("\nHeaders:")
        for key, value in resp.headers.items():
            print(f"{key}: {value}")
            
        # Check for Access-Control-Allow-Origin header
        if "Access-Control-Allow-Origin" in resp.headers:
            if resp.headers["Access-Control-Allow-Origin"] == origin:
                print("\n✅ CORS is properly configured for this origin!")
            else:
                print(f"\n⚠️  CORS allows a different origin: {resp.headers['Access-Control-Allow-Origin']}")
        else:
            print("\n❌ CORS headers are missing!")
            
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    test_api_with_cors("http://127.0.0.1:8000", "http://localhost:5174")
    