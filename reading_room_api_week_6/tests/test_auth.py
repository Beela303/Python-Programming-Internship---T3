def test_register_and_login(client):
    created = client.post("/api/v1/auth/register", json={"email": "a@example.com", "password": "StrongPass123"})
    assert created.status_code == 201
    login = client.post("/api/v1/auth/login", data={"username": "a@example.com", "password": "StrongPass123"})
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"

def test_duplicate_email_returns_409(client):
    payload = {"email": "a@example.com", "password": "StrongPass123"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    assert client.post("/api/v1/auth/register", json=payload).status_code == 409

def test_invalid_credentials_return_401(client):
    assert client.post("/api/v1/auth/login", data={"username": "x@example.com", "password": "wrong"}).status_code == 401
