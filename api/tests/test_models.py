import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.database import Base
from api.models import Task

engine = create_engine('sqlite:///:memory:')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def test_task_model():
    # Setup
    session = SessionLocal()
    new_task = Task(
        title="Test Task",
        description="This is a test task",
        completed=False,
        creator_name="Test User",
        email="testchancy@example.com",
        phone_number="+33689745210",
        deadline=None,
    )

    session.add(new_task)
    session.commit()

    # Verify
    task = session.query(Task).first()
    assert task.title == "Test Task"
    assert task.description == "This is a test task"
    assert task.completed == False
    assert task.creator_name == "Test User"
    assert task.email == "testchancy@example.com"
    assert task.phone_number == "+33689745210"
    assert task.deadline == None

    # Teardown
    session.close()