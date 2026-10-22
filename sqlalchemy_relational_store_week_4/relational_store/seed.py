from sqlalchemy import select

from relational_store.database import create_schema, make_session_factory
from relational_store.models import Author
from relational_store.repositories import AuthorRepository, BookRepository, CustomerRepository


def seed() -> None:
    engine = create_schema()
    SessionFactory = make_session_factory(engine)

    with SessionFactory.begin() as session:
        if session.scalar(select(Author.id).limit(1)) is not None:
            print("Database already contains data; skipping seed.")
            return

        authors = AuthorRepository(session)
        books = BookRepository(session)
        customers = CustomerRepository(session)

        fiction = authors.add("Chimamanda Ngozi Adichie")
        science = authors.add("Carl Sagan")
        books.add(title="Half of a Yellow Sun", author_id=fiction.id, price_cents=2500, stock=8)
        books.add(title="Americanah", author_id=fiction.id, price_cents=2200, stock=5)
        books.add(title="Cosmos", author_id=science.id, price_cents=1800, stock=10)
        customers.add(name="Ada Okafor", email="ada@example.com")
        customers.add(name="Tunde Bello", email="tunde@example.com")

    print("Seed data created.")


if __name__ == "__main__":
    seed()
