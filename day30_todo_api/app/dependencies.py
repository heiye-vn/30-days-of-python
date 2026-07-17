from day30_todo_api.app.repository import TodoRepository

todo_repository = TodoRepository()


def get_todo_repository() -> TodoRepository:
    return todo_repository
