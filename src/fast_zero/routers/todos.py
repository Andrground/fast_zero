from fastapi import APIRouter, Depends
from fast_zero.schemas import (
    TodoSchema,
    TodoPublic,
    TodoList,
    Message,
    TodoUpdate,
)
from fast_zero.database import get_session
from fast_zero.security import get_current_user
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from fast_zero.models import User, Todo, TodoState
from fastapi import HTTPException
from http import HTTPStatus


router = APIRouter(prefix="/todos", tags=["todos"])

Session = Annotated[Session, Depends(get_session)]
Current_user = Annotated[User, Depends(get_current_user)]


@router.post("/", response_model=TodoPublic)
def create_todo(todo: TodoSchema, session: Session, user: Current_user):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo


@router.get("/", response_model=TodoList)
def list_todos(
    session: Session,
    user: Current_user,
    title: str | None = None,
    description: str | None = None,
    state: TodoState | None = None,
    offset: int | None = None,
    limit: int | None = None,
):
    query = select(Todo).where(Todo.user_id == user.id)

    if title:
        query = query.filter(Todo.title.contains(title))
    if description:
        query = query.filter(Todo.description.contains(description))
    if state:
        query = query.filter(Todo.state == state)

    todos = session.scalars(query.offset(offset).limit(limit)).all()
    return {"todos": todos}


@router.delete("/{todo_id}", response_model=Message)
def delete_todo(todo_id: int, session: Session, user: Current_user):
    todo = session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)
    )

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Task not found"
        )

    session.delete(todo)
    session.commit()

    return {"message": "Task deleted successfully"}


@router.patch("/{todo_id}", response_model=TodoPublic)
def patch_todo(
    todo_id: int, session: Session, user: Current_user, todo: TodoUpdate
):
    db_todo = session.scalar(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Task not found"
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo
