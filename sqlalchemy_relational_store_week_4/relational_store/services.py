from sqlalchemy.orm import Session

from relational_store.models import Order, OrderItem
from relational_store.repositories import (
    BookRepository,
    CustomerRepository,
    OrderRepository,
)


class StoreError(Exception):
    """Base class for expected business-rule errors."""


class NotFoundError(StoreError):
    """A referenced record does not exist."""


class InvalidOrderError(StoreError):
    """The requested order is not valid."""


class StoreService:
    """Business operations; persistence details stay in repositories."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.books = BookRepository(session)
        self.customers = CustomerRepository(session)
        self.orders = OrderRepository(session)

    def place_order(
        self, *, customer_id: int, items: list[tuple[int, int]]
    ) -> Order:
        """Create an order atomically from (book_id, quantity) pairs."""
        if not items:
            raise InvalidOrderError("An order must contain at least one item.")

        # One transaction covers validation, stock changes, and order rows.
        with self.session.begin():
            customer = self.customers.get(customer_id)
            if customer is None:
                raise NotFoundError(f"Customer {customer_id} does not exist.")

            # Combine duplicate book IDs before checking stock and creating lines.
            quantities: dict[int, int] = {}
            for book_id, quantity in items:
                if quantity <= 0:
                    raise InvalidOrderError("Quantity must be greater than zero.")
                quantities[book_id] = quantities.get(book_id, 0) + quantity

            order = Order(customer_id=customer_id)
            for book_id, quantity in quantities.items():
                book = self.books.get(book_id)
                if book is None:
                    raise NotFoundError(f"Book {book_id} does not exist.")
                if book.stock < quantity:
                    raise InvalidOrderError(
                        f"Insufficient stock for '{book.title}': "
                        f"requested {quantity}, available {book.stock}."
                    )

                book.stock -= quantity
                order.items.append(
                    OrderItem(
                        book=book,
                        quantity=quantity,
                        unit_price_cents=book.price_cents,
                    )
                )

            self.orders.add(order)
            # IDs and computed values are available before leaving the transaction.
            self.session.flush()
            return order
