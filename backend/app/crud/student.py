from sqlalchemy.orm import Session
from app.models.student import Student




def create_student(db: Session, student_in):
    db_student = Student(**student_in.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student




def get_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Student).offset(skip).limit(limit).all()