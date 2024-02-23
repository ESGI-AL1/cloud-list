from sqlalchemy import Column, String, Boolean, DateTime, Integer
from database import Base


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    description = Column(String(255), index=True)
    completed = Column(Boolean, default=False)
    file_url = Column(String(255), index=True)
    creator_name = Column(String(255), index=True)
    email = Column(String(255), index=True)
    phone_number = Column(String(20), index=True)
    deadline = Column(DateTime, index=True)