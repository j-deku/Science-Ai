from pydantic import BaseModel


class StudentCreate(BaseModel):
    name: str
    age: int
    grade: str | None = None


class StudentRead(BaseModel):
    id: int
    name: str
    age: int
    grade: str | None


class Config:
    orm_mode = True