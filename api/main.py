from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from models import Task
from database import SessionLocal
from schemas import TaskPydantic
from utils import (
    upload_file_cloud_storage,
    trigger_lambda_aws,
    delete_file_from_cloud_storage,
    sign_url,
)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/tasks/", response_model=TaskPydantic)
async def create_task(
    title: str = Form(...),
    description: str = Form(None),
    completed: bool = Form(False),
    creator_name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    deadline: Optional[str] = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date() if deadline else None

    if file:
        file_url = upload_file_cloud_storage(file)

        task = Task(
            title=title,
            email=email,
            description=description,
            completed=completed,
            file_url=file_url,
            creator_name=creator_name,
            phone_number=phone_number,
            deadline=deadline_date,
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        trigger_lambda_aws(phone_number=phone_number, title=title)

        return task


@app.get("/tasks/", response_model=List[TaskPydantic])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = db.query(Task).offset(skip).limit(limit).all()

    for task in tasks:
        task.signed_url = sign_url(task.file_url)

    return tasks


@app.get("/tasks/{task_id}", response_model=TaskPydantic)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.file_url:
        task.signed_url = sign_url(task.file_url)

    return task


@app.put("/tasks/{task_id}", response_model=TaskPydantic)
async def update_task(
    task_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    completed: Optional[bool] = Form(None),
    creator_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    deadline: Optional[str] = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if completed is not None:
        task.completed = completed
    if creator_name is not None:
        task.creator_name = creator_name
    if email is not None:
        task.email = email
    if deadline is not None:
        task.deadline = datetime.strptime(deadline, "%Y-%m-%d").date()
    if file:
        task.file_url = upload_file_cloud_storage(file)

    db.commit()
    db.refresh(task)

    return task


@app.delete("/tasks/{task_id}", response_model=dict)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.file_url:
        delete_file_from_cloud_storage(task.file_url)

    db.delete(task)
    db.commit()

    return {"message": f"Task {task_id} deleted"}
