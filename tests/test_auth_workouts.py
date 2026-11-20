from tests.conftest import register_and_login


def test_register_login_and_me(client):
    headers = register_and_login(client)
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "one@example.com"


def test_duplicate_email_and_bad_password_rejected(client):
    register_and_login(client)
    duplicate = client.post("/api/v1/auth/register", json={
        "email": "one@example.com", "password": "another-safe-password"
    })
    assert duplicate.status_code == 409
    bad_login = client.post("/api/v1/auth/login", json={
        "email": "one@example.com", "password": "wrong-password"
    })
    assert bad_login.status_code == 401


def test_workout_create_list_and_user_isolation(client):
    headers_a = register_and_login(client, "a@example.com")
    headers_b = register_and_login(client, "b@example.com")

    exercise = client.post("/api/v1/exercises", headers=headers_a, json={
        "name": "Bench Press", "muscle_group": "chest", "equipment": "barbell"
    })
    assert exercise.status_code == 201, exercise.text
    exercise_id = exercise.json()["id"]

    workout = client.post("/api/v1/workouts", headers=headers_a, json={
        "performed_at": "2026-10-28",
        "notes": "push day",
        "sets": [
            {"exercise_id": exercise_id, "set_number": 1, "weight": 60, "reps": 8, "rpe": 8},
            {"exercise_id": exercise_id, "set_number": 2, "weight": 60, "reps": 7}
        ]
    })
    assert workout.status_code == 201, workout.text
    workout_id = workout.json()["id"]
    assert len(workout.json()["sets"]) == 2

    own = client.get(f"/api/v1/workouts/{workout_id}", headers=headers_a)
    assert own.status_code == 200
    hidden = client.get(f"/api/v1/workouts/{workout_id}", headers=headers_b)
    assert hidden.status_code == 404

    other_list = client.get("/api/v1/workouts", headers=headers_b)
    assert other_list.status_code == 200
    assert other_list.json() == []

    delete_other = client.delete(f"/api/v1/workouts/{workout_id}", headers=headers_b)
    assert delete_other.status_code == 404
    assert client.get(f"/api/v1/workouts/{workout_id}", headers=headers_a).status_code == 200


def test_auth_required_and_cannot_use_another_users_custom_exercise(client):
    headers_a = register_and_login(client, "a@example.com")
    headers_b = register_and_login(client, "b@example.com")
    assert client.get("/api/v1/workouts").status_code == 401

    exercise = client.post("/api/v1/exercises", headers=headers_a, json={"name": "Private Curl"})
    assert exercise.status_code == 201
    response = client.post("/api/v1/workouts", headers=headers_b, json={
        "performed_at": "2026-10-28",
        "sets": [{"exercise_id": exercise.json()["id"], "set_number": 1, "weight": 10, "reps": 10}]
    })
    assert response.status_code == 422


def test_recovery_fields_remain_optional_and_user_scoped(client):
    headers_a = register_and_login(client, "a@example.com")
    headers_b = register_and_login(client, "b@example.com")
    created = client.post("/api/v1/recovery", headers=headers_a, json={
        "recorded_at": "2026-10-29", "sleep_hours": 7.5
    })
    assert created.status_code == 201, created.text
    assert created.json()["energy_score"] is None
    assert created.json()["soreness_score"] is None
    assert client.get("/api/v1/recovery", headers=headers_b).json() == []


def test_swagger_form_login_token_works(client):
    from tests.conftest import register_and_login
    register_and_login(client, "swagger@example.com")
    response = client.post("/api/v1/auth/token", data={
        "username": "swagger@example.com", "password": "correct-horse-battery"
    })
    assert response.status_code == 200, response.text
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 200
    bad = client.post("/api/v1/auth/token", data={"username": "swagger@example.com", "password": "nope"})
    assert bad.status_code == 401
    schema = client.get("/api/v1/openapi.json").json()
    flow = schema["components"]["securitySchemes"]["OAuth2PasswordBearer"]["flows"]["password"]
    assert flow["tokenUrl"] == "/api/v1/auth/token"
