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
    sections: List[Section]   

class SectionInDB(BaseModel):
    id: int
    course_id: int
    title: str
    content: str
    order_num: int
 
class CourseInDB(BaseModel):
    id: int
    title: str
    description: str
    