#!/usr/bin/env python3
"""
Test HTTP endpoints using requests library.
"""
import requests
import json
import time

def test_endpoints():
    """Test all requirements endpoints via HTTP."""
    base_url = "http://127.0.0.1:8000"

    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(5)

    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        print(f"Health: {response.status_code} - {response.text}")

        # Test requirements endpoint
        print("\nTesting requirements endpoint...")
        response = requests.get(f"{base_url}/api/v1/requirements")
        print(f"Requirements: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} requirements")
            if data:
                print(f"First requirement: {data[0].get('title', 'No title')}")

        # Test categories endpoint
        print("\nTesting categories endpoint...")
        response = requests.get(f"{base_url}/api/v1/requirements/categories")
        print(f"Categories: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} categories")
            if data:
                print(f"First category: {data[0].get('name', 'No name')}")
                category_id = data[0].get('id')

                # Test creating a new requirement
                print("\nTesting create requirement...")
                new_req = {
                    "title": "HTTP Test Requirement",
                    "description": "This is a test requirement via HTTP",
                    "category_id": category_id,
                    "source": "http_test",
                    "created_by": "test-user"
                }
                response = requests.post(f"{base_url}/api/v1/requirements", json=new_req)
                print(f"Create requirement: {response.status_code}")
                if response.status_code in [200, 201]:
                    data = response.json()
                    print(f"Created requirement: {data.get('title', 'No title')}")
                    req_id = data.get('id')

                    # Test getting the specific requirement
                    print(f"\nTesting get requirement {req_id}...")
                    response = requests.get(f"{base_url}/api/v1/requirements/{req_id}")
                    print(f"Get requirement: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"Retrieved requirement: {data.get('title', 'No title')}")

                    # Test updating the requirement
                    print(f"\nTesting update requirement {req_id}...")
                    update_data = {
                        "title": "Updated HTTP Test Requirement",
                        "description": "This is an updated test requirement via HTTP"
                    }
                    response = requests.put(f"{base_url}/api/v1/requirements/{req_id}", json=update_data)
                    print(f"Update requirement: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"Updated requirement: {data.get('title', 'No title')}")

                    # Test deleting the requirement
                    print(f"\nTesting delete requirement {req_id}...")
                    response = requests.delete(f"{base_url}/api/v1/requirements/{req_id}")
                    print(f"Delete requirement: {response.status_code}")
                    if response.status_code == 200:
                        print("Deleted requirement successfully")

    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Make sure the application is running on port 8000.")
    except Exception as e:
        print(f"Error testing endpoints: {e}")

if __name__ == "__main__":
    test_endpoints()
