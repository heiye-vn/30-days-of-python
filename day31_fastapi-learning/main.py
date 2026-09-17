from fastapi import FastAPI

app = FastAPI(title="我的第一个 API", version="0.1.0")

# 模拟数据库
fake_items = {
    1: {"name": "机械键盘", "price": 399.0},
    2: {"name": "显示器", "price": 1299.0},
}

@app.get("/")
def read_root():
    """服务健康检查"""
    return {"message": "Hello, FastAPI!"}

@app.get("/items/{item_id}")
# 函数形参 verbose 不在路径中，FastAPI 会自动将其识别为 Query Parameter，默认值为 False
def read_item(item_id: int, verbose: bool = False):
    """根据 ID 查询商品

    - **item_id**: 商品 ID，必须是整数
    """
    item = fake_items.get(item_id)
    if item is None:
        return {"error": "商品不存在"}
    
    # 构造新的返回字典
    response_data = {"item_id": item_id, **item}
    if verbose:
        response_data["currency"] = "CNY"
    return response_data

@app.post("/items")
def create_item(name: str, price: float):
    """创建商品（简化版，第 4 章会改用请求体）"""
    new_id = max(fake_items) + 1
    fake_items[new_id] = {"name": name, "price": price}
    return {"item_id": new_id, "name": name, "price": price}