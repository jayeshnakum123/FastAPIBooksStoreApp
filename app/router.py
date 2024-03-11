from fastapi import FastAPI, HTTPException, Depends, APIRouter, Request, Form, status
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Book, Signup
from app.schemas import add_book_request, SignupForm, SigninForm
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from app.schemas import UserRole
from app.models import Signup
from datetime import datetime, timedelta
from fastapi import Query
from typing import Optional

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


################################################################################
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# The OAuth2PasswordBearer class is commonly used for authentication in API


#################################################################################
# create JWT Bearer Token Function
def create_access_token(data: dict):
    to_encode = data.copy()
    expiration = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )  # timedelta representing the expiration time for the access token
    to_encode.update({"exp": expiration})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/signin")
async def signin(signinForm: SigninForm):
    db = SessionLocal()
    signin_user = (
        db.query(Signup)
        .filter(
            Signup.username == signinForm.username,
            Signup.password == signinForm.password,
        )
        .first()
    )
    if (
        signin_user is None
        or signin_user.password != signinForm.password
        and signin_user.username != signinForm.username
    ):
        raise HTTPException(status_code=404, detail="Invalid UserName and Password !")

    # Generate a JWT token
    token_data = {"sub": signin_user.username, "role": signin_user.role}
    access_token = create_access_token(token_data)

    return {
        "Message": "User Signin Done!",
        "UserName": signin_user.username,
        "UserRole": signin_user.role,
        "Department": signin_user.department,
        "access_token": access_token,
    }


################################################################################################
# Get Book By Department


def get_current_user_role(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return role


################################################################################################

"""Admin And Student Are Access Books By In Role"""


@router.get("/books/Optional")
async def get_books_based_on_role(
    token: str = Depends(oauth2_scheme),
    department: Optional[str] = Query(None, title="Department"),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = (
        db.query(Signup)
        .filter(Signup.username == username, Signup.role == role)
        .first()
    )
    if user is None:
        raise credentials_exception

    if role == UserRole.admin.value:
        if department:
            # Return all books for the specific department
            books = db.query(Book).filter_by(department=department).all()
        else:
            # Return all books for admin
            books = db.query(Book).all()
    elif role == UserRole.student.value:
        if department and department != user.department:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are not authorized to access books ! your department *{user.department}* only access",
            )
        # Filter books based on the department of the signed-in student
        books = db.query(Book).filter_by(department=user.department).all()
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return {
        "books": [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "price": book.price,
                "year_published": book.year_published,
                "department": book.department,
            }
            for book in books
        ]
    }


#####################################################################################
"""CHECK CONNECTION IS SUCCESSFULL OR NOT !"""


@router.get("/demo")
def demo():
    return {"message": "Connection Successfully !"}


# New Book Added In Database Using PostMan throw!
"""A new book has been added to the database using Postman !"""


@router.post("/add_book/")
async def add_book(
    request: add_book_request,
    db: Session = Depends(get_db),
):
    try:
        # Check if a book with the same title already exists
        existing_book = db.query(Book).filter(Book.title == request.title).first()
        if existing_book:
            raise HTTPException(
                status_code=400,
                detail=f"Book *{existing_book.title}* title already exists",
            )

        # print(request.title)
        new_book = Book(
            title=request.title,
            author=request.author,
            price=request.price,
            year_published=request.year_published,
            department=request.department,
        )
        db.add(new_book)
        db.commit()
        db.refresh(new_book)
        return {"message": "Book added successfully", "book_id": new_book.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# GET ALL BOOKS ! POSTMAN AND ALL SHOW IN BROWSER
"""GET ALL BOOKS ROUTER"""


@router.get("/get_all_books/")
async def get_all_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return {
        "books": [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "price": book.price,
                "year_published": book.year_published,
                "department": book.department,
            }
            for book in books
        ]
    }


"""UPDATE THE ROW IN TABLE"""


@router.put("/update_book/{book_id}")
async def update_book(
    book_id: int, request: add_book_request, db: Session = Depends(get_db)
):
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if book:
            book.title = request.title
            book.author = request.author
            book.price = request.price
            book.year_published = request.year_published
            book.department = request.department
            db.commit()
            return {"message": "Book updated successfully", "book_id": book.id}
        else:
            raise HTTPException(status_code=404, detail="Book not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


"""DELETE THE ROW IN TABLE"""


@router.delete("/delete_book/{book_id}")
async def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
):
    try:
        existing_book = db.query(Book).filter(Book.id == book_id).first()

        if existing_book is None:
            raise HTTPException(status_code=404, detail="Book not found")

        db.delete(existing_book)
        db.commit()

        return {"message": "Book deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


"""GET ONE BOOK DETAIL IN DATABASES !"""


@router.get("/get_book/{book_id}")
async def get_book_details(
    book_id: int,
    db: Session = Depends(get_db),
):
    try:
        book = db.query(Book).filter(Book.id == book_id).first()

        if book is None:
            raise HTTPException(status_code=404, detail="Book not found")

        return {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "price": book.price,
            "year_published": book.year_published,
            "department": book.department,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


#################################################
## user SignUp Data Store in Signup Table using PostMan


@router.post("/signup")
async def signup(signupForm: SignupForm):
    role_str = signupForm.role.value if signupForm.role else None
    new_signup = Signup(
        username=signupForm.username,
        password=signupForm.password,
        role=role_str,
        department=signupForm.department,
    )
    db = SessionLocal()
    db.add(new_signup)
    db.commit()
    db.refresh(new_signup)
    db.close()

    # return signupForm
    return {"Message": "New User Are Created And Save Data In DataBase !"}


## get all username data from table signup


@router.get("/get_user")
async def get_all_user():
    db = SessionLocal()
    user_data = db.query(Signup).all()
    db.close()
    user_data = [
        {
            "id": user.id,
            "UserName": user.username,
            "Password": user.password,
            "Role": user.role,
            "Department": user.department,
        }
        for user in user_data
    ]
    return {"User": user_data}


## delete username
@router.delete("/user_delete/{user_id}")
async def delete_user(user_id: int):
    # Retrieve the user from the database based on the provided user_id
    db = SessionLocal()
    user = db.query(Signup).filter(Signup.id == user_id).first()

    # Check if the user exists
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete the user
    db.delete(user)
    db.commit()
    db.close()

    # Return a success response
    return {"message": "User Delete Successfully !"}


# @router.get("/books_By_role")
# async def get_books_based_on_role(
#     token: str = Depends(oauth2_scheme),
#     db: Session = Depends(get_db),
# ):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         role: str = payload.get("role")
#         if username is None or role is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception

#     user = (
#         db.query(Signup)
#         .filter(Signup.username == username, Signup.role == role)
#         .first()
#     )
#     if user is None:
#         raise credentials_exception

#     if role == UserRole.admin.value:
#         # Return all books for admin
#         books = db.query(Book).all()
#     elif role == UserRole.student.value:
#         # Filter books based on the department of the signed-in student
#         books = db.query(Book).filter_by(department=user.department).all()
#     else:
#         raise HTTPException(status_code=403, detail="Forbidden")

#     return {
#         "books": [
#             {
#                 "id": book.id,
#                 "title": book.title,
#                 "author": book.author,
#                 "price": book.price,
#                 "year_published": book.year_published,
#                 "department": book.department,
#             }
#             for book in books
#         ]
#     }


# ################################################################################################
