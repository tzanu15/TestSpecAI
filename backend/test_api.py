#!/usr/bin/env python3
"""
Test script for API endpoints using httpx.
"""
import asyncio
import httpx
import json

async def test_endpoints():
    """Test all requirements endpoints."""
    base_url = "http://127.0.0.1:8000"

    async with httpx.AsyncClient() as client:
        try:
            # Test health endpoint
            print("Testing health endpoint...")
            response = await client.get(f"{base_url}/health")
            print(f"Health: {response.status_code} - {response.text}")

            # Test requirements endpoint
            print("\nTesting requirements endpoint...")
            response = await client.get(f"{base_url}/api/v1/requirements")
            print(f"Requirements: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Found {len(data)} requirements")
                if data:
                    print(f"First requirement: {data[0].get('title', 'No title')}")

            # Test categories endpoint
            print("\nTesting categories endpoint...")
            response = await client.get(f"{base_url}/api/v1/requirements/categories")
            print(f"Categories: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Found {len(data)} categories")
                if data:
                    print(f"First category: {data[0].get('name', 'No name')}")

            # Test creating a new requirement
            print("\nTesting create requirement...")
            new_req = {
                "title": "Test Requirement",
                "description": "This is a test requirement",
                "category_id": "test-category-id",
                "source": "test"
            }
            response = await client.post(f"{base_url}/api/v1/requirements", json=new_req)
            print(f"Create requirement: {response.status_code}")
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"Created requirement: {data.get('title', 'No title')}")
                return data.get('id')

        except httpx.ConnectError:
            print("Could not connect to server. Make sure the application is running on port 8000.")
            return None
        except Exception as e:
            print(f"Error testing endpoints: {e}")
            return None

if __name__ == "__main__":
    asyncio.run(test_endpoints())
