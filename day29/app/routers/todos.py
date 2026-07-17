from fastapi import APIRouter, FastAPI

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("/")
def list_todos():
    return [{"id": 1, "title": "Learn FastAPI"}, {"id": 2, "title": "Swimming"}]
