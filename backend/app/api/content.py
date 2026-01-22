from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.student import create_student, get_students
from app.schemas.student import StudentCreate, StudentRead

router = APIRouter(prefix="/students", tags=["Students"])

@router.post("/", response_model=StudentRead)
def add_student(student: StudentCreate, db: Session = Depends(get_db)):
    return create_student(db, student)

@router.get("/", response_model=list[StudentRead])
def list_students(db: Session = Depends(get_db)):
    return get_students(db)
