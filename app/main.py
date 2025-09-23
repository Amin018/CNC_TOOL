from fastapi import FastAPI
from app.database import engine
from app import models, database
from app.routers import admin, users, auth, tools, changeover, parts
from fastapi import Depends
from app.routers.auth import get_current_user
from app import schemas
from fastapi.middleware.cors import CORSMiddleware
from app.utils import hash_password

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CNC Tool Management API")

# Create all tables (SQLite file will be created on first run)
models.Base.metadata.create_all(bind=engine)

def seed_admin():
    db = database.SessionLocal()
    if not db.query(models.User).filter(models.User.role == "admin").first():
        admin = models.User(
            username="admin",
            hashed_password=hash_password("admin123"),  # change later
            role="admin",
            full_name="Default Admin"
        )
        db.add(admin)
        db.commit()
        print(" Default admin created: username=admin, password=admin123")
    db.close()

# Call this when app starts
seed_admin()

# 🔥 Allow frontend to talk to backend
origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(tools.router)
app.include_router(auth.router)
app.include_router(changeover.router)
app.include_router(parts.router)

@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/users/me")
def read_users_me(current_user: schemas.UserResponse = Depends(get_current_user)):
    return current_user