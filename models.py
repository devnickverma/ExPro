from pydantic import BaseModel
from typing import List, Optional
from datetime  import datetime

class Section(BaseModel):
    title: str
    content: str
    order_num: int

class Course(BaseModel):
    title: str
    description: str
    sections: List[Section]  # Nested sections within a course

class CourseInDB(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime

class SectionInDB(BaseModel):
    id: int
    course_id: int
    title: str
    content: str
    order_num: int
