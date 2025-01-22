from fastapi import APIRouter, Depends, status, HTTPException
from app.backend.db import Base
from app.backend.db_depends import get_db
from typing import Annotated
from sqlalchemy import Column, Integer, String, insert, select, update, delete
from sqlalchemy.orm import relationship, Session
from sqlalchemy.schema import CreateTable
from app.schemas import CreateUser, UpdateUser
from slugify import slugify

router = APIRouter(prefix="/user", tags=["user"])


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    age = Column(Integer)
    slug = Column(String, unique=True, index=True)

    tasks = relationship("Task", back_populates="user")


print(CreateTable(User.__table__))


@router.get("/")
async def all_users(database: Annotated[Session, Depends(get_db)]):
    users = database.scalars(select(User)).all()
    return users


@router.get("/user_id")
async def user_by_id(user_id: int,
                     database: Annotated[Session, Depends(get_db)]):
    user = database.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User(id={user_id}) is not found"
                            )
    return user


@router.post("/create")
async def create_user(user_data: CreateUser,
                      database: Annotated[Session, Depends(get_db)]):
    user_to_create = insert(User).values(
        username=user_data.username,
        firstname=user_data.firstname,
        lastname=user_data.lastname,
        age=user_data.age,
        slug=user_data.username
    )
    database.execute(user_to_create)
    database.commit()

    return {
        "status_code": status.HTTP_201_CREATED,
        "transaction": "Successful"
    }


@router.put("/update")
async def update_user(user_id: int,
                      user_data: UpdateUser,
                      database: Annotated[Session, Depends(get_db)]):
    user = database.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User(id={user_id}) is not found"
                            )

    data_to_update = (
        update(User).where(User.id == user_id).values(
            firstname=user_data.firstname,
            lastname=user_data.lastname,
            age=user_data.age
        )
    )
    database.execute(data_to_update)
    database.commit()

    return {
        "status_code": status.HTTP_200_OK,
        "transaction": f"User(id={user_id}) has been successfully updated"
    }


@router.delete("/delete")
async def delete_user(user_id: int,
                      database: Annotated[Session, Depends(get_db)]):
    user = database.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User(id={user_id}) is not found"
                            )

    user_to_delete = delete(User).where(User.id == user_id)
    database.execute(user_to_delete)
    database.commit()

    return {
        "status_code": status.HTTP_200_OK,
        "transaction": f"User(id={user_id}) has been successfully deleted"
    }
