import os
import shutil
import uuid
import requests
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy import Column, String, Boolean, DateTime, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from google.cloud.sql.connector import Connector, IPTypes
from pydantic import BaseModel
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


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    creator_name: str
    email: str
    phone_number: str  
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
    phone_number: Optional[str] = None  
    deadline: Optional[datetime] = None

    class Config:
        from_orm = True


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

    deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date() if deadline else None

    file_url = None
    if file:
        task_id = str(uuid.uuid4())
        file_name = f"{task_id}_{file.filename}"

        client = storage.Client()
        bucket = client.bucket("cloudlist-413718.appspot.com")  # Update with your bucket name
        blob = bucket.blob(file_name)

        blob.upload_from_string(file.file.read(), content_type=file.content_type)

        file_url = f"https://storage.googleapis.com/cloudlist-413718.appspot.com/{file_name}"

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
        
        lambda_endpoint = 'https://oypihpxobb.execute-api.eu-west-1.amazonaws.com/dev/'
    
        headers = {
            'Content-Type': 'application/json'
        }
    
        data = {
            'phoneNumber': phone_number,  
            'message': 'A new task has been assigned to you: ' + title
        }
    
        response = requests.post(lambda_endpoint, json=data, headers=headers)
        
        if response.status_code == 200:
            print("Successfully notified about the new task.")
        else:
            print(f"Failed to send notification. Status code: {response.status_code}, Message: {response.text}")
        
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



@app.delete("/tasks/{task_id}", response_model=TaskPydantic)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return task