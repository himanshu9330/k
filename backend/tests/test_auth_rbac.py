"""
Tests for SentinelAI-X Authentication and Role-Based Access Control
"""

def test_auth_registration_and_login(client):
    # Register user
    reg_payload = {
        "username": "analyst_john",
        "email": "john@sentinelai.io",
        "password": "SecurePassword123!",
        "full_name": "John Security",
        "role": "ANALYST"
    }
    reg_res = client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 200
    user_data = reg_res.json()["data"]
    assert user_data["username"] == "analyst_john"

    # Login
    login_payload = {
        "username": "analyst_john",
        "password": "SecurePassword123!"
    }
    login_res = client.post("/api/auth/login", json=login_payload)
    assert login_res.status_code == 200
    token_data = login_res.json()["data"]
    assert "access_token" in token_data
    token = token_data["access_token"]

    # Access /me
    me_res = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    assert me_res.json()["data"]["username"] == "analyst_john"
