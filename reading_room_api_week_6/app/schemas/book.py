from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

BookStatus = Literal["to_read", "reading", "completed"]

class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=120)
    genre: str = Field(min_length=1, max_length=80)
    status: BookStatus = "to_read"
    publication_year: int | None = Field(default=None, ge=0, le=2100)

class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, min_length=1, max_length=120)
    genre: str | None = Field(default=None, min_length=1, max_length=80)
    status: BookStatus | None = None
    publication_year: int | None = Field(default=None, ge=0, le=2100)

class BookRead(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    status: BookStatus
    publication_year: int | None
    model_config = ConfigDict(from_attributes=True)

class BookPage(BaseModel):
    items: list[BookRead]
    total: int
    page: int
    page_size: int
    pages: int
