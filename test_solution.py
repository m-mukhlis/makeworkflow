import requests
import json
import time

API_URL = "http://localhost:8000"


def test_webhooks():
    # Load sample payloads
    with open("tests/sample_payloads.json") as f:
        data = json.load(f)

    results = []

    for i, payload in enumerate(data["payloads"]):
        print(f"\nSending payload {i+1}...")
        response = requests.post(f"{API_URL}/webhook/workitem/updated", json=payload)
        result = response.json()
        results.append(result)
        print(f"Response: {result}")
        time.sleep(0.1)  # Small delay between requests

    # Test getting work item details
    print("\n\nGetting work item 42 details...")
    response = requests.get(f"{API_URL}/workitems/42")
    print(json.dumps(response.json(), indent=2))

    # Test time in state calculation
    print("\n\nCalculating time in state for work item 42...")
    response = requests.get(f"{API_URL}/workitems/42/time-in-state")
    print(json.dumps(response.json(), indent=2))

    # Verify duplicate handling
    print("\n\nDuplicate webhook handling:")
    print(f"Payload 1 processed: {results[0]['processed']}")
    print(f"Payload 4 (duplicate) processed: {results[3]['processed']}")


if __name__ == "__main__":
    # Check if API is running
    try:
        response = requests.get(f"{API_URL}/health")
        print("✓ API is running")
    except Exception as e:
        print("✗ API is not running. Start with: fastapi dev main.py")
        print(f"Error: {e}")
        exit(1)

    test_webhooks()
