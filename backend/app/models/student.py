from sqlalchemy import Column, Integer, String
from app.database import Base


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer)
    grade = Column(String(50), nullable=True)