import pytest
from datetime import datetime
from api.schemas import TaskPydantic

def test_TaskPydantic():
    # Setup
    task_data = {
        "id": 1,
        "title": "Test Task",
        "description": "This is a test task",
        "completed": False,
        "creator_name": "Test User",
        "email": "testchancy@example.com",
        "phone_number": "+33689745210",
        "deadline": datetime.now(),
        "signed_url": "http://example.com",
    }

    task = TaskPydantic(**task_data)

    # Verify
    assert task.id == task_data["id"]
    assert task.title == task_data["title"]
    assert task.description == task_data["description"]
    assert task.completed == task_data["completed"]
    assert task.creator_name == task_data["creator_name"]
    assert task.email == task_data["email"]
    assert task.phone_number == task_data["phone_number"]
    assert task.deadline == task_data["deadline"]
    assert task.signed_url == task_data["signed_url"]