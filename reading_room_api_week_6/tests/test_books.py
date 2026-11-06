def sample_book(title="Dune", genre="Science Fiction"):
    return {"title": title, "author": "Frank Herbert", "genre": genre, "status": "to_read", "publication_year": 1965}

def test_book_crud(client, auth_headers):
    created = client.post("/api/v1/books", json=sample_book(), headers=auth_headers)
    assert created.status_code == 201
    book_id = created.json()["id"]
    assert client.get(f"/api/v1/books/{book_id}", headers=auth_headers).json()["title"] == "Dune"
    updated = client.patch(f"/api/v1/books/{book_id}", json={"status": "reading"}, headers=auth_headers)
    assert updated.status_code == 200
    assert updated.json()["status"] == "reading"
    assert client.delete(f"/api/v1/books/{book_id}", headers=auth_headers).status_code == 204
    assert client.get(f"/api/v1/books/{book_id}", headers=auth_headers).status_code == 404

def test_authentication_is_required(client):
    assert client.get("/api/v1/books").status_code == 401

def test_pagination_and_filters(client, auth_headers):
    client.post("/api/v1/books", json=sample_book("Dune", "Sci-Fi"), headers=auth_headers)
    client.post("/api/v1/books", json=sample_book("Foundation", "Sci-Fi"), headers=auth_headers)
    client.post("/api/v1/books", json=sample_book("Emma", "Classic"), headers=auth_headers)
    response = client.get("/api/v1/books?page=1&page_size=1&genre=Sci-Fi", headers=auth_headers)
    data = response.json()
    assert response.status_code == 200
    assert data["total"] == 2
    assert len(data["items"]) == 1
    assert data["pages"] == 2

def test_users_cannot_access_each_others_books(client, auth_headers):
    created = client.post("/api/v1/books", json=sample_book(), headers=auth_headers)
    other = client.post("/api/v1/auth/register", json={"email": "other@example.com", "password": "StrongPass123"})
    login = client.post("/api/v1/auth/login", data={"username": "other@example.com", "password": "StrongPass123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert client.get(f"/api/v1/books/{created.json()['id']}", headers=headers).status_code == 404


def test_invalid_book_payload_returns_422(client, auth_headers):
    response = client.post(
        "/api/v1/books",
        json={"title": "", "author": "A Writer", "genre": "Fiction"},
        headers=auth_headers,
    )
    assert response.status_code == 422
