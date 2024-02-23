from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class TaskPydantic(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    file_url: Optional[str] = None
    creator_name: str
    email: str
    phone_number: Optional[str] = None
    deadline: Optional[datetime] = None