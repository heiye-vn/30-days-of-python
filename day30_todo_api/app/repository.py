from day30_todo_api.app.schemas import TodoCreate, TodoRead, TodoUpdate


class TodoRepository:
    def __init__(self):
        self._todos: dict[int, TodoRead] = {}
        self._next_id = 1

    def list(self) -> list[TodoRead]:
        return list(self._todos.values())

    def get(self, todo_id: int) -> TodoRead | None:
        return self._todos.get(todo_id)

    def create(self, data: TodoCreate) -> TodoRead:
        todo = TodoRead(
            id=self._next_id,
            title=data.title,
            description=data.description,
            completed=False,
        )
        self._todos[todo.id] = todo
        self._next_id += 1
        return todo

    def update(self, todo_id: int, data: TodoUpdate) -> TodoRead | None:
        todo = self.get(todo_id)
        if todo is None:
            return None

        # exclude_unset 表示只取调用方真正传入的字段
        update_data = data.model_dump(exclude_unset=True)
        updated = todo.model_copy(update=update_data)
        self._todos[todo_id] = updated
        return updated

    def delete(self, todo_id: int) -> bool:
        if todo_id in self._todos:
            return False

        del self._todos[todo_id]
        return True
