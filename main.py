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

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect('users.db')
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
    access_token = create_access_token(data={"sub": user[0]})  # assuming email is at index 0
    print("Access Token:", access_token)
    return {"access_token": access_token, "token_type": "bearer"}
@app.get("/users/me")
def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"email": user[0], "full_name": user[1]}  # Return email and full name

