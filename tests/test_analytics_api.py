from datetime import date, timedelta

from tests.conftest import register_and_login


def test_progress_and_insight_analysis_are_user_scoped(client):
    headers_a = register_and_login(client, "lift@example.com")
    headers_b = register_and_login(client, "other@example.com")
    exercise = client.post("/api/v1/exercises", headers=headers_a, json={"name": "Squat"})
    exercise_id = exercise.json()["id"]

    # Five separate eligible weeks: four baseline weeks at 1000 kg-reps, then 1500.
    current_monday = date.today() - timedelta(days=date.today().weekday())
    first_monday = current_monday - timedelta(weeks=4)
    for i, volume in enumerate([1000, 1000, 1000, 1000, 1500]):
        performed = first_monday + timedelta(weeks=i)
        created = client.post("/api/v1/workouts", headers=headers_a, json={
            "performed_at": performed.isoformat(),
            "sets": [{
                "exercise_id": exercise_id,
                "set_number": 1,
                "weight": float(volume // 10),
                "reps": 10,
            }],
        })
        assert created.status_code == 201, created.text

    progress = client.get(f"/api/v1/analytics/exercises/{exercise_id}", headers=headers_a)
    assert progress.status_code == 200
    assert len(progress.json()["points"]) == 5
    assert progress.json()["eligible_loaded_volume_kg_reps"] == 5500

    analysis = client.post(
        f"/api/v1/insights/analyze?exercise_id={exercise_id}", headers=headers_a
    )
    assert analysis.status_code == 201, analysis.text
    assert analysis.json()["insight_type"] == "volume_spike"
    assert analysis.json()["evidence"]["percentage_change"] == 50
    assert analysis.json()["status"] == "ai_unavailable"

    assert client.get("/api/v1/insights", headers=headers_a).json()[0]["id"] == analysis.json()["id"]
    assert client.get("/api/v1/insights", headers=headers_b).json() == []
    assert client.get(f"/api/v1/analytics/exercises/{exercise_id}", headers=headers_b).status_code == 404


def test_insufficient_history_is_explicit_and_persisted(client):
    headers = register_and_login(client)
    exercise = client.post("/api/v1/exercises", headers=headers, json={"name": "Deadlift"})
    response = client.post(
        f"/api/v1/insights/analyze?exercise_id={exercise.json()['id']}", headers=headers
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["evidence"]["sufficient_data"] is False
    assert payload["confidence"] == "low"
    assert payload["evidence"]["current_value"] is None


def test_future_workout_and_recovery_dates_are_rejected(client):
    headers = register_and_login(client, "future@example.com")
    exercise = client.post("/api/v1/exercises", headers=headers, json={"name": "Row"})
    future = date.today() + timedelta(days=1)
    workout = client.post("/api/v1/workouts", headers=headers, json={
        "performed_at": future.isoformat(),
        "sets": [{"exercise_id": exercise.json()["id"], "set_number": 1, "weight": 20, "reps": 8}],
    })
    assert workout.status_code == 422
    recovery = client.post("/api/v1/recovery", headers=headers, json={"recorded_at": future.isoformat()})
    assert recovery.status_code == 422


def test_performance_anomaly_and_plateau_endpoints_use_user_scoped_workouts(client):
    headers = register_and_login(client, "performance@example.com")
    exercise = client.post("/api/v1/exercises", headers=headers, json={"name": "Bench Press"})
    exercise_id = exercise.json()["id"]
    start = date.today() - timedelta(weeks=8)
    # Six prior sessions establish the anomaly baseline; latest session is a dip.
    for index, weight in enumerate([60, 61, 59, 60, 62, 58, 40]):
        response = client.post("/api/v1/workouts", headers=headers, json={
            "performed_at": (start + timedelta(weeks=index)).isoformat(),
            "sets": [{"exercise_id": exercise_id, "set_number": 1, "weight": weight, "reps": 5}],
        })
        assert response.status_code == 201, response.text

    anomaly = client.get(
        f"/api/v1/analytics/exercises/{exercise_id}/performance-anomaly", headers=headers
    )
    assert anomaly.status_code == 200
    assert anomaly.json()["finding_type"] == "performance_dip"
    assert anomaly.json()["sufficient_data"] is True
    assert anomaly.json()["triggered"] is True

    plateau = client.get(f"/api/v1/analytics/exercises/{exercise_id}/plateau", headers=headers)
    assert plateau.status_code == 200
    assert plateau.json()["observation_count"] == 4
    assert plateau.json()["exercise_id"] == exercise_id


def test_analytics_findings_do_not_expose_another_users_exercise(client):
    owner_headers = register_and_login(client, "owner@example.com")
    other_headers = register_and_login(client, "reader@example.com")
    exercise = client.post("/api/v1/exercises", headers=owner_headers, json={"name": "Private Lift"})
    response = client.get(
        f"/api/v1/analytics/exercises/{exercise.json()['id']}/plateau", headers=other_headers
    )
    assert response.status_code == 404


def test_insights_volume_spike_with_five_weeks_and_clear_evidence(client):
    from datetime import date, timedelta
    from tests.conftest import register_and_login
    headers = register_and_login(client, "spike@example.com")
    ex = client.post("/api/v1/exercises", headers=headers, json={"name": "Squat"}).json()["id"]
    monday = date.today() - timedelta(days=date.today().weekday())

    def log(day, weight):
        r = client.post("/api/v1/workouts", headers=headers, json={
            "performed_at": day.isoformat(),
            "sets": [{"exercise_id": ex, "set_number": 1, "weight": weight, "reps": 10}]})
        assert r.status_code == 201, r.text

    # only current week -> insufficient, with a clear count
    log(monday, 100)
    r = client.post("/api/v1/insights/analyze", headers=headers, params={"exercise_id": ex})
    ev = r.json()["evidence"]
    assert ev["sufficient_data"] is False
    assert ev["prior_weeks_found"] == 0 and ev["prior_weeks_required"] == 4

    for weeks_ago in range(1, 5):
        log(monday - timedelta(weeks=weeks_ago), 50)
    r = client.post("/api/v1/insights/analyze", headers=headers, params={"exercise_id": ex})
    ev = r.json()["evidence"]
    assert ev["sufficient_data"] is True and ev["triggered"] is True
    assert ev["finding_type"] == "volume_spike"
