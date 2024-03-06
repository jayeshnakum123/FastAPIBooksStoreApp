from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Book
from app.database import DATABASE_URL
from app.router import router


app = FastAPI()
app.include_router(router=router)

Base.metadata.create_all(bind=engine)
