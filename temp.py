# import sqlite3

# # # Create and initialize the database
# # def init_db():
# #     conn = sqlite3.connect('users.db')
# #     cursor = conn.cursor()

# #     # Create the users table
# #     cursor.execute('''
# #     CREATE TABLE IF NOT EXISTS users (
# #         id INTEGER PRIMARY KEY AUTOINCREMENT,
# #         email TEXT UNIQUE NOT NULL,
# #         full_name TEXT,
# #         hashed_password TEXT NOT NULL
# #     );
# #     ''')

# #     conn.commit()
# #     conn.close()
# #     print("Database initialized successfully")

# # # Run the database initialization
# # init_db()


# def create_tables():
#     conn = sqlite3.connect('users.db')
#     # conn = get_db_connection()
#     cursor = conn.cursor()
    
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS courses (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             title TEXT NOT NULL,
#             description TEXT NOT NULL,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     ''')
    
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS sections (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             course_id INTEGER NOT NULL,
#             title TEXT NOT NULL,
#             content TEXT NOT NULL,
#             order_num INTEGER NOT NULL,
#             FOREIGN KEY (course_id) REFERENCES courses(id)
#         )
#     ''')
    
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS enrollments (
#             user_id INTEGER NOT NULL,
#             course_id INTEGER NOT NULL,
#             FOREIGN KEY (user_id) REFERENCES users(id),
#             FOREIGN KEY (course_id) REFERENCES courses(id),
#             PRIMARY KEY (user_id, course_id)
#         )
#     ''')
    
#     conn.commit()
#     conn.close()

# # Call the function to create tables on app startup
# create_tables()


import sqlite3

# Create and initialize the database
def create_tables():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Create the courses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
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
        )
    ''')

    # Create the enrollments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrollments (
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(id),
            PRIMARY KEY (user_id, course_id)
        )
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
        )
    ''')

    conn.commit()
    conn.close()

# Call the function to create tables on app startup
create_tables()