from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
import uuid
import shutil

app = FastAPI()


class Task(BaseModel):
    id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    completed: bool = False
    file_url: Optional[str] = None
    creator_name: str  # Add this line


tasks = {}


@app.get("/tasks/", response_model=List[Task])
async def get_all_tasks(limit: int = 15):
    return list(tasks.values())[:limit]


@app.post("/tasks/", response_model=Task)
async def create_task(title: str = Form(...), description: str = Form(None), completed: bool = Form(False), creator_name: str = Form(...), file: UploadFile = File(None)):
    task_id = uuid.uuid4()
    file_url = None
    if file:
        file_location = f"files/{task_id}_{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_url = f"http://localhost:8000/{file_location}"
    task = Task(id=task_id, title=title, description=description, completed=completed, file_url=file_url, creator_name=creator_name)
    tasks[task_id] = task.dict()
    return task


@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: uuid.UUID):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: uuid.UUID, title: str = Form(None), description: str = Form(None),
                      completed: bool = Form(None), creator_name: str = Form(None), file: UploadFile = File(None)):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]
    if title:
        task['title'] = title
    if description:
        task['description'] = description
    if completed is not None:
        task['completed'] = completed
    if creator_name:
        task['creator_name'] = creator_name
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
