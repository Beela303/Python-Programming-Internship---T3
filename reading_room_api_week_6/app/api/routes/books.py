from math import ceil
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.book import Book
from app.models.user import User
from app.schemas.book import BookCreate, BookPage, BookRead, BookUpdate

router = APIRouter()

def owned_book(db: Session, book_id: int, user_id: int) -> Book:
    book = db.scalar(select(Book).where(Book.id == book_id, Book.owner_id == user_id))
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    book = Book(**payload.model_dump(), owner_id=user.id)
    db.add(book)
    db.commit()
    db.refresh(book)
    return book

@router.get("", response_model=BookPage)
def list_books(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    genre: str | None = Query(None, min_length=1),
    book_status: str | None = Query(None, alias="status", pattern="^(to_read|reading|completed)$"),
    search: str | None = Query(None, min_length=1, max_length=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    filters = [Book.owner_id == user.id]
    if genre:
        filters.append(Book.genre.ilike(f"%{genre}%"))
    if book_status:
        filters.append(Book.status == book_status)
    if search:
        term = f"%{search}%"
        filters.append(or_(Book.title.ilike(term), Book.author.ilike(term)))
    total = db.scalar(select(func.count()).select_from(Book).where(*filters)) or 0
    items = db.scalars(select(Book).where(*filters).order_by(Book.id.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return BookPage(items=items, total=total, page=page, page_size=page_size, pages=ceil(total / page_size) if total else 0)

@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return owned_book(db, book_id, user.id)

@router.patch("/{book_id}", response_model=BookRead)
def update_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    book = owned_book(db, book_id, user.id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    book = owned_book(db, book_id, user.id)
    db.delete(book)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
