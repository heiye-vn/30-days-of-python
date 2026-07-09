from typing import Literal, NotRequired, Optional, Protocol, TypedDict, Union


def add(a: int, b: int) -> int:
    return a + b


# print(add(1, 2))
# print(add(1.5, 2))

# ... 在元组注解中表示不定长
numbers: tuple[int, ...] = (1, 2, 3, 4, 5)


# Union 或 |：联合类型
# def normalize_id(value: Union[int, float]) -> str:
def normalize_id(value: int | float) -> str:
    return str(value)


# Optional: 可能为 None
def find_user(user_id: int) -> Optional[str]:
    # def find_user(user_id: int) -> str | None:
    if user_id == 1:
        return "Alice"
    return None


# Literal: 限定具体取值
Mode = Literal["read", "write", "append"]


def open_resource(mode: Mode) -> None:
    print(f"打开模式：{mode}")


# open_resource("write")


class User(TypedDict):
    name: str
    email: str
    age: int


def send_email(user: User) -> None:
    print(f"发送邮件给 {user['name']}: {user['email']}")


user1: User = {"name": "Alice", "email": "alice@example.com", "age": 20}

# send_email(user1)


class UserProfile(TypedDict):
    name: str
    email: str
    bio: NotRequired[str]  # 可选字段


"""
Protocol: 按能力描述类型，类似 “鸭子” 类型
它让你可以定义一个"接口"，只要一个类实现了这个接口里声明的方法和属性，
就自动被视为该 Protocol 的子类型——不需要显式继承
"""


class Tool(Protocol):
    name: str
    description: str

    def execute(self, **kwargs): ...


class WebSearchTool:
    name = "web_search"
    description = "互联网信息搜索工具"

    def execute(self, **kwargs) -> str:  # noqa
        query = kwargs.get("query", "")
        return f"搜索结果：{query}"


class CalculatorTool:
    name = "calculator"
    description = "数学计算工具"

    def execute(self, **kwargs) -> str:  # noqa
        expr = kwargs.get("expression", "0")
        return str(eval(expr))


# 这两个类都没有显式继承 Tool，
# 但都实现了 Tool 协议，所以可以传给这个函数：
def invoke_tool(tool: Tool) -> str:
    print(f"调用工具：{tool.name} - {tool.description}")
    return tool.execute(**{})  # noqa
