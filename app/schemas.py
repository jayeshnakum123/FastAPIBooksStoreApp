from pydantic import BaseModel, validator

from app.models import UserRole


# Add Books
"""Add Books Using Validator Schemas"""


class add_book_request(BaseModel):
    title: str
    author: str
    price: int
    year_published: int
    department: str

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

    @validator("department")
    def validate_department(cls, value):
        valid_department = ["Eng", "Arts", "Comm"]
        if value not in valid_department:
            raise ValueError(
                f"Invalid Add Department ! '{value}' Department Add Only {valid_department}"
            )
        return value


# User Signup schemas
"""SignUpForm Validator"""


class SignupForm(BaseModel):
    username: str
    password: str
    role: UserRole  # Using Roll Are Access Is UsingRole Class Enum
    department: str

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

    @validator("role")
    def validate_role(cls, value):
        try:
            return UserRole(value)  # Using Roll Are Access Is UsingRole Class Enum
        except ValueError:
            raise ValueError(f"Invalid role: {value}")

    @validator("department")
    def validate_department(cls, value):
        valid_department = ["admin", "Eng", "Arts", "Comm"]
        if value not in valid_department:
            raise ValueError(
                f"Invalid Department! '{value}' is not a valid department. Valid departments are: {', '.join(valid_department)}"
            )
        return value


# User Signin schemas


class SigninForm(BaseModel):
    username: str
    password: str
