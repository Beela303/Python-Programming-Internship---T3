"""Small executable API walkthrough using an isolated in-memory database."""
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db.base import Base
from app.db.session import get_db
from app.main import app

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
def override_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
app.dependency_overrides[get_db] = override_db

with TestClient(app) as client:
    print("1. Register:", client.post("/api/v1/auth/register", json={"email":"demo@example.com","password":"DemoPass123"}).status_code)
    token = client.post("/api/v1/auth/login", data={"username":"demo@example.com","password":"DemoPass123"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("2. Login: access token issued")
    book = client.post("/api/v1/books", headers=headers, json={"title":"Things Fall Apart","author":"Chinua Achebe","genre":"Fiction","status":"reading","publication_year":1958})
    print("3. Create book:", book.status_code, book.json())
    print("4. List books:", client.get("/api/v1/books?page=1&page_size=10", headers=headers).json())
    print("5. Health:", client.get("/health").json())
app.dependency_overrides.clear()
Base.metadata.drop_all(engine)
