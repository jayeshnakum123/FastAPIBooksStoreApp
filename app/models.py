from sqlalchemy import Column, Integer, String, MetaData
from app.database import Base
from app.database import DATABASE_URL
from app.database import SessionLocal, engine, Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    price = Column(Integer)
    year_published = Column(Integer)


books = Book


class Signup(Base):
    __tablename__ = "signup"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(length=100), unique=True)
    password = Column(String(length=255))
