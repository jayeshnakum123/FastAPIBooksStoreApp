from fastapi import FastAPI, HTTPException, Depends, APIRouter, Request, Form
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Book, Signup
from app.schemas import add_book_request, SignupForm, SigninForm


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


"""CHECK CONNECTION IS SUCCESSFULL OR NOT !"""


@router.get("/demo")
def demo():
    return {"message": "Connection successfully"}


# New Book Added In Database Using PostMan throw!
"""A new book has been added to the database using Postman !"""


@router.post("/add_book/")
async def add_book(
    request: add_book_request,
    db: Session = Depends(get_db),
):
    try:
        # print(request.title)
        new_book = Book(
            title=request.title,
            author=request.author,
            price=request.price,
            year_published=request.year_published,
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
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


#################################################
## user SignUp Data Store in Signup Table using PostMan


@router.post("/signup")
async def signup(signupForm: SignupForm):
    new_signup = Signup(username=signupForm.username, password=signupForm.password)
    db = SessionLocal()
    db.add(new_signup)
    db.commit()
    db.refresh(new_signup)
    db.close()

    # return signupForm
    return {"Message": "New User Are Created And Save Data In DataBase !"}


## user Signin Using Table Signup using postman


@router.get("/signin")
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

    return {"Message": "User Signin Done ! "}


## get all username data from table signup


@router.get("/get_user")
async def get_all_user():
    db = SessionLocal()
    user_data = db.query(Signup).all()
    db.close()
    user_data = [user.username for user in user_data]
    return {"UserName": user_data}


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