from fastapi import APIRouter, Depends, status, HTTPException
from app.backend.db_depends import get_db
from typing import Annotated
from sqlalchemy import select, Table, MetaData
from sqlalchemy.orm import Session
from app.schemas import CreateTask, UpdateTask
from slugify import slugify
# model imports below
from app.backend.db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    priority = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    slug = Column(String, unique=True, index=True)

    user = relationship("User", back_populates="tasks")


# print(CreateTable(Task.__table__))

router = APIRouter(prefix="/task", tags=["task"])


@router.get("/")
async def all_tasks(database: Annotated[Session, Depends(get_db)]):

    tasks = database.scalars(select(Task)).all()
    return tasks


@router.get("/task_id")
async def task_by_id(task_id: int,
                     database: Annotated[Session, Depends(get_db)]):

    task = database.scalar(select(Task).where(Task.id == task_id))

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task(id={task_id}) is not found")
    return task


@router.post("/create")
async def create_task(task_data: CreateTask,
                      user_id: int,
                      database: Annotated[Session, Depends(get_db)]):
    metadata = MetaData()
    users_table = Table("users", metadata, autoload_with=database.bind)

    user = database.scalar(select(users_table).where(users_table.c.id == user_id))

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User(id={user_id}) is not found")

    slug = slugify(task_data.title)
    new_task = Task(
        title=task_data.title,
        content=task_data.content,
        priority=task_data.priority,
        user_id=user_id,
        slug=slug
    )

    database.add(new_task)
    database.commit()

    return {
        "status_code": status.HTTP_201_CREATED,
        "transaction": "Successful"
    }


@router.put("/update")
async def update_task(task_id: int,
                      task_data: UpdateTask,
                      database: Annotated[Session, Depends(get_db)]):

    task = database.scalar(select(Task).where(Task.id == task_id))

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task(id={task_id}) is not found")

    task.title = task_data.title,
    task.content = task_data.content,
    task.priority = task_data.priority

    database.commit()

    return {
        "status_code": status.HTTP_200_OK,
        "transaction": f"Task(id={task_id}) has been successfully updated"
    }


@router.delete("/delete")
async def delete_task(task_id: int,
                      database: Annotated[Session, Depends(get_db)]):
    task = database.scalar(select(Task).where(Task.id == task_id))

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task(id={task_id}) is not found")

    database.delete(task)
    database.commit()

    return {
        "status_code": status.HTTP_200_OK,
        "transaction": f"Task(id={task_id}) has been successfully deleted!"
    }
