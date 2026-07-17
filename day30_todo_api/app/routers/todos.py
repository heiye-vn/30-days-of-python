from fastapi import APIRouter, Depends, HTTPException, Response, status

from day30_todo_api.app.dependencies import get_todo_repository
from day30_todo_api.app.repository import TodoRepository
from day30_todo_api.app.schemas import TodoCreate, TodoRead, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("/", response_model=list[TodoRead])
def list_todos(repo: TodoRepository = Depends(get_todo_repository)):
    return repo.list()


@router.post("/", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(data: TodoCreate, repo: TodoRepository = Depends(get_todo_repository)):
    return repo.create(data)


@router.get("/{todo_id}", response_model=TodoRead)
def get_todo(todo_id: int, repo: TodoRepository = Depends(get_todo_repository)):
    todo = repo.get(todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="待办事项不存在"
        )

    return todo


@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(
    todo_id: int, data: TodoUpdate, repo: TodoRepository = Depends(get_todo_repository)
):
    todo = repo.update(todo_id, data)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="待办事项不存在"
        )

    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, repo: TodoRepository = Depends(get_todo_repository)):
    deleted = repo.delete(todo_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="待办事项不存在")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
