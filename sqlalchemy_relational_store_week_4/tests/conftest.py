import pytest

from relational_store.database import create_schema, make_session_factory
from relational_store.repositories import AuthorRepository, BookRepository, CustomerRepository


@pytest.fixture
def session_factory(tmp_path):
    db_path = tmp_path / "test_store.db"
    engine = create_schema(f"sqlite:///{db_path}")
    factory = make_session_factory(engine)
    yield factory
    engine.dispose()


@pytest.fixture
def seeded_ids(session_factory):
    with session_factory.begin() as session:
        author = AuthorRepository(session).add("Test Author")
        book = BookRepository(session).add(
            title="Test Book", author_id=author.id, price_cents=1299, stock=3
        )
        customer = CustomerRepository(session).add(
            name="Test Customer", email="test@example.com"
        )
        ids = {"author_id": author.id, "book_id": book.id, "customer_id": customer.id}
    return ids
