#!/usr/bin/env python3
"""
Test script for API endpoints using FastAPI TestClient.
"""
import asyncio
from fastapi.testclient import TestClient
from app.main import app

def test_endpoints():
    """Test all requirements endpoints using TestClient."""
    client = TestClient(app)
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response = client.get("/health")
        print(f"Health: {response.status_code} - {response.text}")

        # Test requirements endpoint
        print("\nTesting requirements endpoint...")
        response = client.get("/api/v1/requirements")
        print(f"Requirements: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} requirements")
            if data:
                print(f"First requirement: {data[0].get('title', 'No title')}")

        # Test categories endpoint
        print("\nTesting categories endpoint...")
        response = client.get("/api/v1/requirements/categories")
        print(f"Categories: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} categories")
            if data:
                print(f"First category: {data[0].get('name', 'No name')}")
                return data[0].get('id')

        # Test creating a new requirement
        print("\nTesting create requirement...")
        new_req = {
            "title": "Test Requirement",
            "description": "This is a test requirement",
            "category_id": "test-category-id",
            "source": "test"
        }
        response = client.post("/api/v1/requirements", json=new_req)
        print(f"Create requirement: {response.status_code}")
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"Created requirement: {data.get('title', 'No title')}")
            return data.get('id')

    except Exception as e:
        print(f"Error testing endpoints: {e}")
        return None

if __name__ == "__main__":
    test_endpoints()
