# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.api import user, student, ai, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Science AI Platform")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # FRONTEND URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(student.router)
app.include_router(ai.router)
app.include_router(admin.router)  # Admin routes under /ai/admin
