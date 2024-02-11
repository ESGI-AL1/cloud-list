import os
import shutil
import uuid

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy import Column, String, Boolean, DateTime, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from google.cloud.sql.connector import Connector, IPTypes
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


Base = declarative_base()
connector = Connector()


def init_connection_pool(connector: Connector):
    def getconn():
        conn = connector.connect(
            "cloudlist-413718:europe-west2:sql-cloudlist",
            "pymysql",
            user="sql-cloudlist",
            password="cloudlist-esgi!",
            db="todos",
            ip_type=IPTypes.PUBLIC
        )
        return conn

    engine = create_engine("mysql+pymysql://", creator=getconn)
    return engine


engine = init_connection_pool(connector)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    description = Column(String(255), index=True)
    completed = Column(Boolean, default=False)
    file_url = Column(String(255), index=True)
    creator_name = Column(String(255), index=True)
    email = Column(String(255), index=True)
    deadline = Column(DateTime, index=True)


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    creator_name: str
    email: str
    deadline: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    creator_name: Optional[str] = None
    email: Optional[str] = None
    deadline: Optional[datetime] = None


class TaskPydantic(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    file_url: Optional[str] = None
    creator_name: str
    email: str
    deadline: Optional[datetime] = None

    class Config:
        orm_mode = True


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/tasks/", response_model=TaskPydantic)  # Adjusted to use TaskPydantic for response model
async def create_task(title: str = Form(...),
                      description: str = Form(None),
                      completed: bool = Form(False),
                      creator_name: str = Form(...),
                      email: str = Form(...),
                      deadline: Optional[str] = Form(None),
                      file: UploadFile = File(None),
                      db: Session = Depends(get_db)):
    deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date() if deadline else None

    file_url = None
    if file:
        task_id = str(uuid.uuid4())
        file_location = f"files/{task_id}_{file.filename}"
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_url = f"http://localhost:8000/{file_location}"

    task = Task(title=title, email=email, description=description, completed=completed,
                file_url=file_url, creator_name=creator_name, deadline=deadline_date)

    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/tasks/", response_model=List[TaskPydantic])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = db.query(Task).offset(skip).limit(limit).all()
    return tasks


@app.get("/tasks/{task_id}", response_model=TaskPydantic)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=TaskPydantic)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    for var, value in vars(task_update).items():
        if value is not None:
            setattr(task, var, value)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", response_model=TaskPydantic)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return task
