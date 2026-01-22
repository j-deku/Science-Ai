from pydantic import BaseModel


class ContentCreate(BaseModel):
    title: str
    body: str
    source: str | None = None


class ContentRead(BaseModel):
    id: int
    title: str
    body: str
    source: str | None


class Config:
    orm_mode = True