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
    

class MarkSectionCompletedRequest(BaseModel):
    section_id: int

class MarkSectionCompletedResponse(BaseModel):
    success: bool
    message: str

from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SectionCompletion(Base):
    __tablename__ = 'section_completions'

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey('sections.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    completed = Column(Boolean, default=False)

    section = relationship("Section", back_populates="completions")
    user = relationship("User", back_populates="completed_sections")