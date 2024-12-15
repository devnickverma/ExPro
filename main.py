from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import sqlite3
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# FastAPI app initialization
app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup the templates directory
templates = Jinja2Templates(directory="templates")

# Secret key and algorithm for JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300
    

 
# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from typing import Annotated
@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


# Database helper functions
def get_db_connection():
    conn = sqlite3.connect('expro_database.db')
    return conn

def get_user_by_email(email: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user_in_db(user_create: BaseModel, hashed_password: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (email, full_name, hashed_password) VALUES (?, ?, ?)",
                   (user_create.email, user_create.full_name, hashed_password))
    conn.commit()
    conn.close()

# Utility functions
def get_password_hash(password: str):
    return pwd_context.hash(password)



def validate_token_refresh(token: str):
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token does not contain a valid user ID"
            )
        
        # Here, you can validate the user against your database if necessary
        # For example, by checking if the user exists in the 'users' table:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return payload  # Return the decoded token information, including user_id

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# API endpoint to check user validity
@app.get("/api/check_user")
async def check_user(request: Request):
    # Get token from the Authorization header
    token = request.headers.get('Authorization')
    print(token)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing"
        )

    # Remove "Bearer " prefix from the token string
    token = token.split(" ")[1] if token.startswith("Bearer ") else token

    # Validate token and check user
    try:
        print(token)
        user = validate_token(token)
        print("User: ", user)
        return {"status": "valid", "user_id": user["user_id"]}  # Return user ID and valid status
    except HTTPException as e:
        # Return error if the token is invalid
        return {"status": "invalid", "detail": str(e.detail)}


# API endpoint to check user validity
@app.get("/api/check_admin")
async def check_admin(request: Request):
    # Get token from the Authorization header
    token = request.headers.get('Authorization')
    print(token)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing"
        )

    # Remove "Bearer " prefix from the token string
    token = token.split(" ")[1] if token.startswith("Bearer ") else token

    # Validate token and check user
    try:
        print(token)
        user = validate_token(token)
        print("User: ", user)
        new_user = get_user_by_email(user["user_email"])
        print(new_user)
        if new_user[4]:
            return {"status": "valid", "user_id": user["user_id"], "is_admin":  new_user[4]}  # Return user ID and valid status
        return {"status": "invalid"}  
    except HTTPException as e:
        # Return error if the token is invalid
        return {"status": "invalid", "detail": str(e)}


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(email: str, password: str):
    user = get_user_by_email(email)
    print(user)
    if not user or not verify_password(password, user[3]):  # assuming the hashed password is at index 2
        return False
    return user

# User models
class User(BaseModel):
    email: str
    full_name: Optional[str] = None
    hashed_password: str

class UserCreate(BaseModel):
    email: str
    full_name: Optional[str] = None
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "ExPro"})

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/hello")        
def root():
    return {"message": "Hello World"}

@app.post("/signup", response_model=User)
async def signup(user_create: UserCreate):
    if get_user_by_email(user_create.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_create.password)
    create_user_in_db(user_create, hashed_password)
    
    return User(email=user_create.email, full_name=user_create.full_name, hashed_password=hashed_password)

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
   
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,           
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print("User:", user)
    user_id = user[0]
    user_email = user[1]
    access_token = create_access_token(
        data={"user_id": user_id, "user_email": user_email}
    )  
    
    return {"access_token": access_token, "token_type": "   "}


@app.get("/users/me")
def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("user_email")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"email": user[0], "full_name": user[1]}  # Return email and full name

from models import *
from datetime import datetime

@app.post("/api/courses/", response_model=CourseInDB)
async def create_course(course: Course):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insert course data
    cursor.execute("INSERT INTO courses (title, description) VALUES (?, ?)",
                   (course.title, course.description))
    course_id = cursor.lastrowid
    
    # Insert sections for the course
    print(course)
    for section in course.sections:
        cursor.execute("INSERT INTO sections (course_id, title, content, order_num) VALUES (?, ?, ?, ?)",
                       (course_id, section.title, section.content, section.order_num))
    
    conn.commit()
    conn.close()
    
    return CourseInDB(id=course_id, title=course.title, description=course.description, created_at=str(datetime.utcnow()), sections=course.sections)


from fastapi import HTTPException, Depends
from typing import List
from pydantic import BaseModel
 



# Define a function to validate the token
def validate_token(token: str):
    try:
        print(token)
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/api/listcourses/", response_model=List[CourseInDB])
async def list_courses(token: Annotated[str, Depends(oauth2_scheme)]):
    # Validate the token first
    payload = validate_token(token)
    
    print("Token payload:", payload)
    
    # Extract email from payload
    email = str(payload.get("user_email", ""))
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Get user from the database using the email
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get a list of courses the user is enrolled in
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT course_id FROM enrollments WHERE user_id = ?", (user[0],))
    enrolled_courses = {course[0] for course in cursor.fetchall()}  # A set of course_ids the user is enrolled in
    
    # Get all courses
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()
    
    courses_out = []
    for course in courses:
        course_id, title, description, created_at = course
        # Skip courses the user is already enrolled in
        if course_id in enrolled_courses:
            continue
        
        # Get sections for the course
        cursor.execute("SELECT * FROM sections WHERE course_id = ?", (course_id,))
        sections = cursor.fetchall()
        
        sections_out = [SectionInDB(id=s[0], course_id=s[1], title=s[2], content=s[3], order_num=s[4]) for s in sections]
        
        courses_out.append(CourseInDB(id=course_id, title=title, description=description, created_at=created_at, sections=sections_out))
    
    conn.close()
    print("courses_out:", courses_out)
    return courses_out

 
from pydantic import BaseModel

# Define Pydantic model for the request body
class EnrollmentRequest(BaseModel):
    course_id: int

@app.post("/enroll/")
async def enroll_in_course(request: EnrollmentRequest, token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        # Decode the JWT token
        print(token, type(token))
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)  # Inspect the payload to check the structure of "sub"
        
        # Ensure the "sub" claim is a string
        email: str = str(payload.get("user_email", ""))
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if the user is already enrolled
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM enrollments WHERE user_id = ? AND course_id = ?", (user[0], request.course_id))
        enrollment = cursor.fetchone()
        if enrollment:
            raise HTTPException(status_code=400, detail="User is already enrolled in this course")
        
        # Enroll the user
        cursor.execute("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", (user[0], request.course_id))
        conn.commit()
        conn.close()
        
        return {"message": "User enrolled successfully"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTClaimsError as e:
        raise HTTPException(status_code=401, detail=f"JWT error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
@app.post("/users/enroll_courses", response_model=List[CourseInDB])
async def get_enrolled_courses(token: str = Depends(oauth2_scheme)):
    # Validate the token
    payload = validate_token(token)
    email = payload.get("user_email")
    
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get user by email
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch courses the user is enrolled in
    cursor.execute("""
        SELECT c.id, c.title, c.description FROM courses c
        JOIN enrollments e ON c.id = e.course_id
        WHERE e.user_id = ?
    """, (user[0],))
    
    courses = cursor.fetchall()
    
    conn.close()

    # Convert the fetched courses to the Pydantic model
    courses_out = [CourseInDB(id=course[0], title=course[1], description=course[2]) for course in courses]
    
    return courses_out



 
 

def get_course_by_id(course_id):
    # Example using SQLite
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    course = cursor.fetchone()
    
    cursor.execute("SELECT * FROM sections WHERE course_id = ?", (course_id,))
    sections = cursor.fetchall()
    
    conn.close()
    
    return {
        "id": course[0],
        "title": course[1],
        "description": course[2],
        "sections": [{"title": s[2], "content": s[3]} for s in sections]
    }


@app.get("/view/courses", response_class=HTMLResponse)
async def courses(request: Request):
    return templates.TemplateResponse("courses.html", {"request": request})


@app.get("/view/courses/details", response_class=HTMLResponse)
async def courese_deatils(request: Request):
    return templates.TemplateResponse("courses_details.html", {"request": request})


 
 
# # Function to check if the user is an admin


 
# from fastapi import HTTPException

# @app.get("/view/courses/create", response_class=HTMLResponse)
# async def courses_create(request: Request, token: Annotated[str, Depends(oauth2_scheme)]):
#     try:
#         payload = validate_token(token)
#         user_id = get_user_by_email(payload["user_email"])
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Invalid token or user")

#     if is_admin(user_id):
#         return templates.TemplateResponse("create_course.html", {"request": request})

#     return templates.TemplateResponse("login.html", {"request": request})


@app.get("/view/mycourses", response_class=HTMLResponse)
async def my_courses(request: Request):
    return templates.TemplateResponse("mycourses.html", {"request": request})

@app.get("/view/coursedetails", response_class=HTMLResponse)
async def course_details(request: Request):
    return templates.TemplateResponse("course_details.html", {"request": request})

@app.get("/view/courses/details/{course_id}", response_class=HTMLResponse)
async def course_details(request: Request, course_id: int):
    # Fetch course details from the database by course_id
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch course data
    cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
    course = cursor.fetchone()
    
    # Fetch course sections
    cursor.execute("SELECT * FROM sections WHERE course_id = ?", (course_id,))
    sections = cursor.fetchall()
    
    conn.close()
    
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Construct course details response
    course_details = {
        "course_id": course[0],
        "title": course[1],
        "description": course[2],
        "sections": [{"id": section[0], "title": section[2], "content": section[3]} for section in sections]
    }
    
    # Pass the course details to the frontend template
    return templates.TemplateResponse("courses_details.html", {"request": request, "course": course_details})

 
from pydantic import BaseModel

class MarkSectionCompletedRequest(BaseModel):
    section_id: int


@app.post("/api/mark_section_completed/")
async def mark_section_completed(
    request: MarkSectionCompletedRequest,
    token: Annotated[str, Depends(oauth2_scheme)]
):
    # Validate the token
    payload = validate_token(token)
    email = payload.get("user_email", "")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Get the user from the database
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the section is already marked as completed
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM completed_sections WHERE user_id = ? AND section_id = ?",
        (user[0], request.section_id),
    )
    completed = cursor.fetchone()

    if completed:
        raise HTTPException(
            status_code=400,
            detail="Section already marked as completed"
        )

    # Mark the section as completed
    cursor.execute(
        "INSERT INTO completed_sections (user_id, section_id) VALUES (?, ?)",
        (user[0], request.section_id),
    )
    conn.commit()
    conn.close()

    return {"message": "Section marked as completed successfully"}


@app.post("/api/completed_sections/")
async def get_completed_sections(   
    token: Annotated[str, Depends(oauth2_scheme)]
):
    user = validate_token(token)
    user_id = user["user_id"]


    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT section_id 
        FROM completed_sections 
        WHERE user_id = ?
    ''', (user_id,))
    completed_sections = cursor.fetchall()
    conn.close()
    print(completed_sections)
    # Prepare a dictionary of completed section IDs
    completed_dict = {row[0]: True for row in completed_sections}
    return completed_dict




from fastapi import HTTPException
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.get("/view/courses/create", response_class=HTMLResponse)
async def courses_create(request: Request):
    # if not token:
    #     raise HTTPException(status_code=401, detail="Not authenticated111")
    
    # logging.debug(f"Token received: {token}")
    
    # try:
    #     payload = validate_token(token)
    #     user_id = get_user_by_email(payload["user_email"])
    # except Exception as e:
    #     raise HTTPException(status_code=401, detail="Invalid token or user")
    
    # if is_admin(user_id):
    #     return templates.TemplateResponse("create_course.html", {"request": request})

    # return templates.TemplateResponse("login.html", {"request": request})
    return templates.TemplateResponse("create_course.html", {"request": request})