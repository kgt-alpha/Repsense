"""Diagnose a Gemini API key without printing it. Run inside the api container:
    docker compose cp check_key.py api:/app/check_key.py
    docker compose exec api python check_key.py
"""
import json
import os
import urllib.error
import urllib.request

key = os.getenv("GEMINI_API_KEY", "")
print("length:", len(key), "| starts with:", key[:3], "| has quotes/spaces:",
      any(c in key for c in " \"'\t\r\n"))
print("(normal AI Studio keys start with 'AIza' (39 chars) or 'AQ.' (longer))\n")

BASE = "https://generativelanguage.googleapis.com/v1beta"


def call(url, body=None):
    req = urllib.request.Request(url, data=body, headers={
        "x-goog-api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read())["error"]
            reason = (err.get("details") or [{}])[0].get("reason", "")
            return e.code, f"{err.get('status')} {reason}"
        except Exception:
            return e.code, ""


print("list models        ->", *call(f"{BASE}/models"))
payload = json.dumps({"contents": [{"parts": [{"text": "Reply only: OK"}]}]}).encode()
for model in ("gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash"):
    print(f"{model:18} ->", *call(f"{BASE}/models/{model}:generateContent", payload))