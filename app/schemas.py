from pydantic import BaseModel, validator


# Add Books
class add_book_request(BaseModel):
    title: str
    author: str
    price: int
    year_published: int

    @validator("title")
    def validate_title(cls, value):
        if not value or not value.strip():
            raise ValueError("Title cannot be empty or whitespace.")
        return value

    @validator("author")
    def validate_author(cls, value):
        if not value or not value.strip():
            raise ValueError("Author cannot be empty or whitespace.")
        return value

    @validator("price")
    def validate_price(cls, value):
        if value <= 0:
            raise ValueError("Price must be greater than zero.")
        return value

    @validator("year_published")
    def validate_year_published(cls, value):
        current_year = 2024  # Update with the current year or get it dynamically
        if value < 0 or value > current_year:
            raise ValueError(
                f"Invalid year. Year must be between 0 and {current_year}."
            )
        return value


# User Signup schemas
class SignupForm(BaseModel):
    username: str
    password: str

    @validator("username")
    def validate_username(cls, value):
        if len(value) < 3:
            raise ValueError("Username must be at least 3 characters long")
        return value

    @validator("password")
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return value


# User Signin schemas
class SigninForm(BaseModel):
    username: str
    password: str
