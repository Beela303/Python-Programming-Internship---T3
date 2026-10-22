import pytest
from sqlalchemy import func, select

from relational_store.models import Book, Order, OrderItem
from relational_store.services import InvalidOrderError, StoreService


def test_place_order_updates_stock_and_snapshots_price(session_factory, seeded_ids):
    with session_factory() as session:
        service = StoreService(session)
        order = service.place_order(
            customer_id=seeded_ids["customer_id"],
            items=[(seeded_ids["book_id"], 2)],
        )
        order_id = order.id
        assert order.total_cents == 2598

    with session_factory() as session:
        book = session.get(Book, seeded_ids["book_id"])
        saved_order = session.get(Order, order_id)
        line = session.scalar(select(OrderItem).where(OrderItem.order_id == order_id))
        assert book is not None and book.stock == 1
        assert saved_order is not None
        assert line is not None and line.unit_price_cents == 1299
        # The order total comes from line-item snapshots.
        assert saved_order.total_cents == 2598


def test_insufficient_stock_rolls_back_everything(session_factory, seeded_ids):
    with session_factory() as session:
        service = StoreService(session)
        with pytest.raises(InvalidOrderError, match="Insufficient stock"):
            service.place_order(
                customer_id=seeded_ids["customer_id"],
                items=[(seeded_ids["book_id"], 4)],
            )

    with session_factory() as session:
        book = session.get(Book, seeded_ids["book_id"])
        order_count = session.scalar(select(func.count()).select_from(Order))
        line_count = session.scalar(select(func.count()).select_from(OrderItem))
        assert book is not None and book.stock == 3
        assert order_count == 0
        assert line_count == 0


def test_duplicate_book_lines_are_combined(session_factory, seeded_ids):
    with session_factory() as session:
        order = StoreService(session).place_order(
            customer_id=seeded_ids["customer_id"],
            items=[(seeded_ids["book_id"], 1), (seeded_ids["book_id"], 1)],
        )
        assert len(order.items) == 1
        assert order.items[0].quantity == 2


def test_zero_quantity_is_rejected(session_factory, seeded_ids):
    with session_factory() as session:
        with pytest.raises(InvalidOrderError, match="greater than zero"):
            StoreService(session).place_order(
                customer_id=seeded_ids["customer_id"],
                items=[(seeded_ids["book_id"], 0)],
            )


def test_repository_lists_books_with_author(session_factory, seeded_ids):
    from relational_store.repositories import BookRepository

    with session_factory() as session:
        books = BookRepository(session).list_with_authors()
        assert len(books) == 1
        assert books[0].author.name == "Test Author"
