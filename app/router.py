from fastapi import (
    FastAPI,
    HTTPException,
    Depends,
    APIRouter,
    Request,
    Form,
    status,
    Query,
)

from fastapi import Request
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Book, Signup
from app.schemas import add_book_request, SignupForm, SigninForm
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from app.schemas import UserRole
from app.models import Signup
from datetime import datetime, timedelta

# from fastapi import Query
from typing import Optional
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from fastapi.responses import FileResponse
from fastapi import Header

from fastapi import Response

# from fastapi.responses import RedirectResponse

from typing import Optional
from fastapi import Query
from sqlalchemy import or_

router = APIRouter()

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


"""**************************************************************************"""


#### Templates Routers Start In Admin Side And This Is The Admin Home Page Like IndexPage!


@router.get("/get_index")
async def get_index():
    return FileResponse("templates/index.html")


@router.get("/studentBook")
async def student_book(
    request: Request,
    department: Optional[str] = Query(None, alias="department"),
    db: Session = Depends(get_db),
):
    # If department is None, fetch all books
    if not department:
        books = db.query(Book).all()
    else:
        # If only one department is provided, fetch books for that department
        if "," not in department:
            books = db.query(Book).filter(Book.department == department).all()
        else:
            # If multiple departments are provided, fetch books for each department
            departments = department.split(",")
            books = (
                db.query(Book)
                .filter(or_(*[Book.department == d for d in departments]))
                .all()
            )

    return templates.TemplateResponse(
        "studentBook.html", {"request": request, "books": books}
    )


@router.post("/studentBook")
async def studentBook():
    return FileResponse("templates/studentBook.html")


@router.get("/logout")
async def logout(response: Response):
    # Clear access token cookie
    response.delete_cookie(key="access_token")
    # Redirect to signin page
    return RedirectResponse(url="/")  # signin_page


"""8888888888888888888888"""


@router.get("/")  # /signin_page
async def get_signin_page():
    return FileResponse("templates/signin.html")


"""88888888888888888888888888"""


"""**************************************************************************"""


# Add Pagination to user_data endpoint
@router.get("/user-data")
async def user_data(
    request: Request, page: int = Query(default=1), db: Session = Depends(get_db)
):
    # per_page = 10
    per_page = 8
    start = (page - 1) * per_page
    end = start + per_page

    # Fetch user data from the database for the current page
    user_data = db.query(Signup).offset(start).limit(per_page).all()

    if not user_data:
        raise HTTPException(status_code=404, detail="No user data found")

    total_users = db.query(Signup).count()
    total_pages = (total_users - 1) // per_page + 1

    return templates.TemplateResponse(
        "user_data.html",
        {
            "request": request,
            "user_data": user_data,
            "total_pages": total_pages,
            "current_page": page,
        },
    )


"""**************************************************************************"""


# Define edit  Routers In Admin Side
@router.get("/edit/{user_id}")
async def edit_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    # Fetch the user from the database
    user = db.query(Signup).filter(Signup.id == user_id).first()

    # Check if the user exists
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Render the edit user page with the user data
    return templates.TemplateResponse(
        "edit_user.html", {"request": request, "user": user}
    )


# ##post Request Edit Page Routers In Admin Side !
@router.post("/edit/{user_id}")
async def edit_user(
    user_id: int,
    request: Request,  # Move this non-default argument before the default arguments
    username: str = Form(...),
    role: str = Form(..., description="User role (student, admin, teacher)"),
    department: str = Form(..., description="User department (Eng, Arts, Comm)"),
    db: Session = Depends(get_db),
):
    # Validate role and department against predefined values
    valid_roles = ["student", "admin", "teacher"]
    valid_departments = ["Eng", "Arts", "Comm"]

    errors = []

    if role.lower() not in valid_roles:
        errors.append("Invalid role. Enter only student, admin, or teacher.")

    if department not in valid_departments:
        errors.append("Invalid department. Enter only Eng, Arts, or Comm.")

    if errors:
        # Fetch the user from the database
        user = db.query(Signup).filter(Signup.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Render the edit user page with the user data and error messages
        return templates.TemplateResponse(
            "edit_user.html", {"request": request, "user": user, "errors": errors}
        )

    # Fetch the user from the database
    user = db.query(Signup).filter(Signup.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the user details
    user.username = username
    user.role = role
    user.department = department.split(",")

    # Commit changes to the database
    db.commit()

    # Redirect to user_data.html after successfully editing the user
    return RedirectResponse(url="/user-data", status_code=303)


"""**************************************************************************"""


# delete user Record Routers In Admin Side
@router.get("/delete/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    # Fetch the user from the database
    user = db.query(Signup).filter(Signup.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete the user from the database
    db.delete(user)
    db.commit()

    # Redirect to user_data.html after successfully deleting the user
    return RedirectResponse(url="/user-data", status_code=303)


"""**************************************************************************"""


# Add New Book Admin Site & Open A New Page
@router.get("/add_book_admin")
async def add_book_admin(request: Request):  #
    return templates.TemplateResponse("AddNewBook.html", {"request": request})  #


# Send The New Book Data using Post Method
@router.post("/add_book_admin")
async def add_book_admin(
    request: Request,
    title: str = Form(...),
    author: str = Form(...),
    price: str = Form(...),
    year_published: int = Form(...),
    department: str = Form(...),
    db: Session = Depends(get_db),
):
    new_book = Book(
        title=title,
        author=author,
        price=price,
        year_published=year_published,
        department=department,
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return templates.TemplateResponse("index.html", {"request": request})
    # return RedirectResponse(url="/")
    # return {"Message": "Book added successfully !"}


"""**************************************************************************"""


# Route to show all books for admin with pagination
@router.get("/show_all_book_admin")
async def show_all_book_admin(
    request: Request, page: int = 1, per_page: int = 8, db: Session = Depends(get_db)
):
    # Calculate offset
    offset = (page - 1) * per_page
    # Fetch books with pagination
    admin_book = db.query(Book).offset(offset).limit(per_page).all()
    total_books = db.query(Book).count()
    total_pages = -(
        -total_books // per_page
    )  # Ceiling division to calculate total pages
    return templates.TemplateResponse(
        "showAllBookAdmin.html",
        {
            "request": request,
            "admin_book": admin_book,
            "total_pages": total_pages,
            "page": page,
        },
    )


# @router.get("/show_all_book_admin")
# async def show_all_book_admin(request: Request, db: Session = Depends(get_db)):
#     admin_book = db.query(Book).all()
#     return templates.TemplateResponse(
#         "showAllBookAdmin.html", {"request": request, "admin_book": admin_book}
#     )


"""**************************************************************************"""

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


@router.post("/signin")  # User signin
async def signin(
    signinForm: SigninForm,
    db: Session = Depends(get_db),
):
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
        or signin_user.username != signinForm.username
    ):
        raise HTTPException(
            status_code=404,
            detail="Invalid UserName and Password! Please try again.",
        )

    # Generate a JWT token
    token_data = {"sub": signin_user.username, "role": signin_user.role}
    access_token = create_access_token(token_data)

    # Determine the redirect URL based on user role
    if signin_user.role == UserRole.admin.value:
        redirect_url = "/get_index"
    elif signin_user.role == UserRole.student.value:
        redirect_url = f"/studentBook?department={','.join(signin_user.department)}"
    elif signin_user.role == UserRole.teacher.value:
        redirect_url = f"/studentBook?department={','.join(signin_user.department)}"
    else:
        # Handle other roles if necessary
        raise HTTPException(status_code=403, detail="Forbidden")

    # Redirect to the appropriate page based on user role upon successful sign-in
    response = RedirectResponse(url=redirect_url)

    # Set access token as a cookie in the response
    response.set_cookie(key="access_token", value=access_token)

    return response

    # return {
    #     "Message": "User Signin Done!",
    #     "UserName": signin_user.username,
    #     "UserRole": signin_user.role,
    #     "Department": signin_user.department,
    #     "access_token": access_token,
    # }


################################################################################################


def get_current_user_role(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials You Are Token ! Session Are Expired GoTo SignIn",
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


def get_current_username(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials You Are Token ! Session Are Expired GoTo SignIn",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


################################################################################################

"""Admin And Student Are Access Books By In Role"""


@router.get("/get_books_by_user")
async def get_books_by_user(
    current_user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username),
    authorization: str = Header(...),
):
    try:
        # Validate access token
        if authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            role = payload.get("role")
        else:
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header. Please provide a valid access token.",
            )

        if current_user_role == UserRole.admin.value:
            books = db.query(Book).all()
        elif current_user_role == UserRole.student.value:
            # Retrieve the user from the database based on the provided username
            user = db.query(Signup).filter(Signup.username == username).first()

            # Check if the user exists
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")

            # Retrieve books based on the user's department
            books = db.query(Book).filter(Book.department.in_(user.department)).all()

        elif current_user_role == UserRole.teacher.value:
            # Retrieve the user from the database based on the provided username
            user = db.query(Signup).filter(Signup.username == username).first()

            # Check if the user exists
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")

            # Retrieve books based on the user's department
            books = db.query(Book).filter(Book.department.in_(user.department)).all()
        else:
            raise HTTPException(status_code=403, detail="Forbidden")

        # Format the books as needed
        formatted_books = [
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

        return {"books": formatted_books}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


#####################################################################################
"""CHECK CONNECTION IS SUCCESSFULL OR NOT !"""


@router.get("/demo")
def demo():
    return {"message": "Connection Successfully !"}


##############################################################################
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


##############################################################################

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


##############################################################################

"""UPDATE THE BOOK IN TABLE"""


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


##############################################################################
"""DELETE THE BOOK IN TABLE"""


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


##############################################################################
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


##############################################################################
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


##############################################################################
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


#################################################################################################
