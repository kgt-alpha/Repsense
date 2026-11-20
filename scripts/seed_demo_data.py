"""Seed a demo account with five consecutive weeks of workouts for one exercise.

Usage (API must be running):
    python scripts/seed_demo_data.py --email demo@example.com --password demo-password-123 --spike

--spike makes the current week ~50% higher than the baseline so the volume-spike rule triggers.
"""
import argparse
import os
from datetime import date, timedelta

import httpx

API = os.getenv("REPSENSE_API_URL", "http://localhost:8000").rstrip("/")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", default="demo@example.com")
    parser.add_argument("--password", default="demo-password-123")
    parser.add_argument("--exercise", default="Demo Squat")
    parser.add_argument("--spike", action="store_true", help="make the current week a volume spike")
    args = parser.parse_args()

    with httpx.Client(base_url=API, timeout=15.0) as client:
        client.post("/api/v1/auth/register", json={"email": args.email, "password": args.password})
        login = client.post("/api/v1/auth/login", json={"email": args.email, "password": args.password})
        login.raise_for_status()
        client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"

        existing = client.get("/api/v1/exercises").json()
        match = next((e for e in existing if e["name"] == args.exercise), None)
        if match is None:
            created = client.post("/api/v1/exercises", json={"name": args.exercise, "muscle_group": "legs"})
            created.raise_for_status()
            match = created.json()

        today = date.today()
        this_monday = today - timedelta(days=today.weekday())
        for weeks_ago in range(4, -1, -1):
            monday = this_monday - timedelta(weeks=weeks_ago)
            day = min(monday, today)  # never log into the future
            weight = 60 + (4 - weeks_ago) * 2.5
            if weeks_ago == 0 and args.spike:
                weight = 100
            sets = [{"exercise_id": match["id"], "set_number": n, "weight": weight, "reps": 8}
                    for n in range(1, 5)]
            response = client.post("/api/v1/workouts", json={
                "performed_at": day.isoformat(), "notes": "demo seed", "sets": sets,
            })
            response.raise_for_status()
            print(f"Logged {day} · {weight} kg x 8 x 4")
    print("Done. Open Insights in the dashboard and analyze:", args.exercise)


if __name__ == "__main__":
    main()
