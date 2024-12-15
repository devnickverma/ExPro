import sqlite3

def get_db_connection(db_name='expro_database.db'):
    """Establish and return a database connection."""
    return sqlite3.connect(db_name)

def init_db():
    """Initialize the database with the `users` table."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        full_name TEXT,
        hashed_password TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE
    );
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully")

def create_tables():
    """Create additional tables for courses, sections, enrollments, and completed sections."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create the courses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Create the sections table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        order_num INTEGER NOT NULL,
        FOREIGN KEY (course_id) REFERENCES courses(id)
    );
    ''')

    # Create the enrollments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS enrollments (
        user_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (course_id) REFERENCES courses(id),
        PRIMARY KEY (user_id, course_id)
    );
    ''')

    # Create the completed_sections table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS completed_sections (
        user_id INTEGER NOT NULL,
        section_id INTEGER NOT NULL,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (section_id) REFERENCES sections(id),
        PRIMARY KEY (user_id, section_id)
    );
    ''')

    conn.commit()
    conn.close()
    print("Tables created successfully")

if __name__ == "__main__":
    # Initialize the database and create tables on script run
    init_db()
    create_tables()
