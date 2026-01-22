from sqlalchemy import Column, Integer, String, Text
from app.database import Base


class Content(Base):
    __tablename__ = "contents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)