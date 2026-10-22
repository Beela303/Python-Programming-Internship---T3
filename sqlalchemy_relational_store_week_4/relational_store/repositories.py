from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from relational_store.models import Author, Book, Customer, Order, OrderItem


class AuthorRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, name: str) -> Author:
        author = Author(name=name.strip())
        self.session.add(author)
        self.session.flush()
        return author

    def get(self, author_id: int) -> Author | None:
        return self.session.get(Author, author_id)


class BookRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(
        self, *, title: str, author_id: int, price_cents: int, stock: int
    ) -> Book:
        book = Book(
            title=title.strip(),
            author_id=author_id,
            price_cents=price_cents,
            stock=stock,
        )
        self.session.add(book)
        self.session.flush()
        return book

    def get(self, book_id: int) -> Book | None:
        return self.session.get(Book, book_id)

    def list_with_authors(self) -> list[Book]:
        statement = select(Book).options(selectinload(Book.author)).order_by(Book.title)
        return list(self.session.scalars(statement))


class CustomerRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, *, name: str, email: str) -> Customer:
        customer = Customer(name=name.strip(), email=email.strip().lower())
        self.session.add(customer)
        self.session.flush()
        return customer

    def get(self, customer_id: int) -> Customer | None:
        return self.session.get(Customer, customer_id)


class OrderRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, order: Order) -> Order:
        self.session.add(order)
        self.session.flush()
        return order

    def get_with_items(self, order_id: int) -> Order | None:
        statement = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items).selectinload(OrderItem.book))
        )
        return self.session.scalar(statement)
