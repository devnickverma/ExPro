import sqlite3
from passlib.context import CryptContext

# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash the password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Connect to the SQLite database
conn = sqlite3.connect('expro_database.db')  # Replace with the actual database path
cursor = conn.cursor()

# Create users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        full_name TEXT,
        hashed_password TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE
    );
''')

# Function to create an admin user
def create_admin_user(email: str, full_name: str, password: str):
    hashed_password = hash_password(password)
    
    cursor.execute('''
        INSERT INTO users (email, full_name, hashed_password, is_admin)
        VALUES (?, ?, ?, ?)
    ''', (email, full_name, hashed_password, True))  # is_admin = True for admin user
    
    conn.commit()

# Example: Create an admin user (replace with your desired details)
create_admin_user('admin@test.com', 'Admin User', 'admin')

print("Admin user created successfully!")

# Close the connection
conn.close()
