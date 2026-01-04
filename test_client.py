import requests
import json

# Test the TP server endpoints
base_url = "http://localhost:8000"

print("Testing TP Server...")

# Test health endpoint
try:
    response = requests.get(f"{base_url}/api/health")
    print(f"Health check: {response.json()}")
except Exception as e:
    print(f"Health check failed: {e}")

# Create a test user
try:
    user_data = {"username": "testuser"}
    response = requests.post(f"{base_url}/api/users", json=user_data)
    if response.status_code == 200:
        user = response.json()
        print(f"Created user: {user}")
        user_id = user["id"]
    else:
        print(f"User creation failed: {response.status_code} - {response.text}")
        user_id = 1  # Use default user
except Exception as e:
    print(f"User creation failed: {e}")
    user_id = 1

# Create a test beatmap
try:
    beatmap_data = {
        "beatmap_id": 1,
        "title": "Test Beatmap",
        "artist": "Test Artist",
        "creator": "Test Creator",
        "star_rating": 3.5
    }
    response = requests.post(f"{base_url}/api/beatmaps", json=beatmap_data)
    if response.status_code == 200:
        beatmap = response.json()
        print(f"Created beatmap: {beatmap}")
        beatmap_id = beatmap["beatmap_id"]
    else:
        print(f"Beatmap creation failed: {response.status_code} - {response.text}")
        beatmap_id = 1
except Exception as e:
    print(f"Beatmap creation failed: {e}")
    beatmap_id = 1

# Submit a test score
try:
    score_data = {
        "user_id": user_id,
        "beatmap_id": beatmap_id,
        "raw_score": 1000000,
        "accuracy": 0.95,
        "count_300": 300,
        "count_100": 50,
        "count_50": 20,
        "count_miss": 30,
        "mods": "HD,DT"
    }
    response = requests.post(f"{base_url}/api/scores/submit", json=score_data)
    if response.status_code == 200:
        score = response.json()
        print(f"Submitted score: {score}")
    else:
        print(f"Score submission failed: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Score submission failed: {e}")

# Get leaderboard
try:
    response = requests.get(f"{base_url}/api/leaderboards/beatmap/{beatmap_id}")
    if response.status_code == 200:
        leaderboard = response.json()
        print(f"Leaderboard: {leaderboard}")
    else:
        print(f"Leaderboard retrieval failed: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Leaderboard retrieval failed: {e}")

print("Test completed!")
