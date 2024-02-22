import os
import uuid
import requests
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, status
from sqlalchemy import Column, String, Boolean, DateTime, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from google.cloud.sql.connector import Connector, IPTypes
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from google.cloud import storage
from fastapi.middleware.cors import CORSMiddleware

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

class TaskORM(Base):
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

class Task(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)
    creator_name: str
    email: Optional[str]
    phone_number: Optional[str] = None
    deadline: Optional[datetime] = None

    class Config:
        orm_mode = True

app = FastAPI()

origins = [
    "http://localhost:4200",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
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


@app.post("/tasks/", response_model=Task)
async def create_task(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    completed: bool = Form(False),
    creator_name: str = Form(...),
    email: str = Form(...),
    phone_number: Optional[str] = Form(None),
    deadline: Optional[datetime] = Form(None),
    file: Optional[UploadFile] = File(description="Upload a file"),
    db: Session = Depends(get_db),
):
    
    deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date() if deadline else None
    file_url = None
    
    if file:
        file_name = f"{uuid.uuid4()}_{file.filename}"
        bucket_name = "cloudlist-413718.appspot.com"  

        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.upload_from_string(await file.read(), content_type=file.content_type)
        
        file_url = f"https://storage.googleapis.com/cloudlist-413718.appspot.com/{file_name}"
        
    task = TaskORM(
        title=title,
        description=description,
        completed=completed,
        creator_name=creator_name,
        email=email,
        phone_number=phone_number,
        deadline=deadline_date,
        file_url=file_url
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    if phone_number:
        lambda_endpoint = 'https://oypihpxobb.execute-api.eu-west-1.amazonaws.com/dev/'
        headers = {'Content-Type': 'application/json'}
        data = {
            'phoneNumber': phone_number,
            'message': f'A new task has been assigned to you: {title}'
        }
        response = requests.post(lambda_endpoint, json=data, headers=headers)
        if response.status_code == 200:
            print("Successfully notified about the new task.")
        else:
            print(f"Failed to send notification. Status code: {response.status_code}, Message: {response.text}")

    return task


@app.get("/tasks/", response_model=List[Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = db.query(TaskORM).offset(skip).limit(limit).all()
    return tasks


@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    completed: Optional[bool] = Form(None),
    creator_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    deadline: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    task = db.query(TaskORM).filter(TaskORM.id == task_id).first()
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
        task.deadline = datetime.strptime(deadline, '%Y-%m-%d').date()

    if file:
        file_name = f"{uuid.uuid4()}_{file.filename}"
        bucket_name = "cloudlist-413718.appspot.com"  

        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        blob.upload_from_string(await file.read(), content_type=file.content_type)

        task.file_url = f"https://storage.googleapis.com/{bucket_name}/{file_name}"

    db.commit()
    db.refresh(task)
    return task



@app.delete("/tasks/{task_id}", response_model=Task)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return task