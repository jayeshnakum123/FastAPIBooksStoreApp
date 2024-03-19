from sqlalchemy import Column, Integer, String, MetaData, Enum, ARRAY
from app.database import Base
from app.database import DATABASE_URL
from app.database import SessionLocal, engine, Base
from enum import Enum
from sqlalchemy.ext.declarative import declarative_base

"""Create Table Book Using Models"""


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(length=255), unique=True)
    author = Column(String(length=255))
    price = Column(Integer)
    year_published = Column(Integer)
    department = Column(String(length=255))


books = Book

"""Create User Role"""


class UserRole(Enum):
    admin = "admin"
    student = "student"
    teacher = "teacher"


"""Create Table SignUp"""


class Signup(Base):
    __tablename__ = "signup"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(length=100), unique=True)
    password = Column(String(length=255))
    role = Column(String(length=50))
    department = Column(ARRAY(String(length=255)))
