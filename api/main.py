from datetime import date, datetime
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
import uuid
import shutil
from fastapi.middleware.cors import CORSMiddleware
from pydantic.v1 import validator


app = FastAPI(
    title="Cloud-list API",
    description="A simple to-do list using cloud services",
    version="0.0.1")


origins = [
    "http://localhost:4200",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Task(BaseModel):
    id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    completed: bool = False
    file_url: Optional[str] = None
    creator_name: str
    email: str


tasks = {}


@validator('deadline', pre=True, allow_reuse=True)
def deadline_not_in_past(cls, v):
    if v is not None and datetime.strptime(v, '%Y-%m-%d').date() < datetime.now().date():
        raise ValueError("Deadline date cannot be in the past")
    return v


@app.get("/tasks/", response_model=List[Task])
async def get_all_tasks(limit: int = 15):
    return list(tasks.values())[:limit]


@app.post("/tasks/", response_model=Task)
async def create_task(title: str = Form(...),
                      description: str = Form(None),
                      completed: bool = Form(False),
                      creator_name: str = Form(...),
                      email: str = Form(...),
                      deadline: Optional[str] = Form(None),
                      file: UploadFile = File(None)):
    task_id = uuid.uuid4()
    file_url = None
    deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date() if deadline else None
    if file:
        file_location = f"files/{task_id}_{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_url = f"http://localhost:8000/{file_location}"
    task = Task(id=task_id, title=title, email=email, description=description, completed=completed,
                file_url=file_url, creator_name=creator_name, deadline=deadline_date)
    tasks[task_id] = task.dict()
    return task


@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: uuid.UUID):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: uuid.UUID,
                      title: str = Form(None),
                      description: str = Form(None),
                      completed: bool = Form(None),
                      creator_name: str = Form(None),
                      email: str = Form(None),
                      deadline: Optional[str] = Form(None),
                      file: UploadFile = File(None)):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]
    if title is not None:
        task['title'] = title
    if description is not None:
        task['description'] = description
    if completed is not None:
        task['completed'] = completed
    if creator_name is not None:
        task['creator_name'] = creator_name
    if email is not None:
        task['email'] = email
    if deadline:
        deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
        task['deadline'] = deadline_date
    if file:
        file_location = f"files/{task_id}_{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        task['file_url'] = f"http://localhost:8000/{file_location}"

    tasks[task_id] = task
    return task


@app.delete("/tasks/{task_id}", response_model=Task)
async def delete_task(task_id: uuid.UUID):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks.pop(task_id)
