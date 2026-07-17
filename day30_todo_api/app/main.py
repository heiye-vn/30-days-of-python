import uvicorn
from fastapi import FastAPI

from day30_todo_api.app.routers import todos

app = FastAPI(
    title="Todo API",
    description="一个用于学习 FastAPI 的待办事项接口项目",
    version="0.1.0",
)

app.include_router(todos.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


# 直接在 mian 中启动服务，适用开发环境，生产环境还是用命令启动
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
