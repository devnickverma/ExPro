import sqlite3

# Create and initialize the database
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create the users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        full_name TEXT,
        hashed_password TEXT NOT NULL
    );
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully")

# Run the database initialization
init_db()