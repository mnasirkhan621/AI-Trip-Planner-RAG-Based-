import requests
import json
import time

url = "http://127.0.0.1:8000/plan_trip"
payload = {"query": "Plan a 2-day trip to Paris"}
headers = {"Content-Type": "application/json"}

# Retry logic in case server is still starting
max_retries = 3
for i in range(max_retries):
    try:
        print(f"Attempt {i+1}...")
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            break
        elif response.status_code == 500:
            # If 500, we want to see the error details and stop retrying blindly unless it looks transient (unlikely for 500)
            break
            
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)
