# ExPro - Course Management System

ExPro is a web-based application designed to manage and display courses. The application is built using Python, FastAPI, and other dependencies to create a robust and scalable solution for course management. 

## Setup Instructions

Follow the steps below to set up and run the ExPro project locally.

### Prerequisites

- Python 3.11 or higher
- Git

### Installation Steps

1. **Clone the repository:**

   First, clone the repository to your local machine using Git:

   ```bash
   git clone <repository-url>
   ```

2. **Check Python version:**

   Ensure that you have Python 3.12 or higher installed:

   ```bash
   python --version
   ```

   If the version is below 3.11, download and install the appropriate Python version from [here](https://www.python.org/downloads/).

3. **Set up a virtual environment:**

   Create a virtual environment for the project:

   ```bash
   python -m venv venv
   ```

4. **Activate the virtual environment:**

   On Windows:

   ```bash
   source ./venv/Scripts/activate
   ```

   On macOS/Linux:

   ```bash
   source ./venv/bin/activate
   ```

5. **Install dependencies:**

   Install the required Python packages using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

6. **Create the database:**

   Run the following commands to create the necessary database and admin user:

   ```bash
   python create_db.py
   python admin_create.py
   ```

7. **Run the application:**

   Start the FastAPI server with Uvicorn:

   ```bash
   uvicorn main:app --reload
   ```

   The application will be running locally at [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Project Features

- **Course Management:** Add, Enrollment,, and view courses.
- **Admin Panel:** Manage the application and create admin users.
  
### View Courses

To view the courses, visit the following URL after starting the app:

[http://127.0.0.1:8000](http://127.0.0.1:8000)


