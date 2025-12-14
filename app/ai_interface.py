# app/ai_interface.py
"""
Cloud AI interface:
- Call user's cloud model (if configured)
- Fallback to local model in local_model.py
"""
import requests, json
from config import AI_CLOUD_ENDPOINT, AI_CLOUD_KEY

def call_cloud_ai(features):
    if not AI_CLOUD_ENDPOINT:
        return None
    payload = {"features": features}
    headers = {"Content-Type":"application/json"}
    if AI_CLOUD_KEY:
        headers["Authorization"] = f"Bearer {AI_CLOUD_KEY}"
    try:
        resp = requests.post(AI_CLOUD_ENDPOINT, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            # Expect response like {"score": 0.45}
            return float(data.get("score", 0.0))
        else:
            print("AI cloud status", resp.status_code, resp.text)
            return None
    except Exception as e:
        print("Cloud call error", e)
        return None
