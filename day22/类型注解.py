from typing import Literal, Optional, Union


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
# def find_user(user_id: int) -> Optional[str]:
def find_user(user_id: int) -> str | None:
    if user_id == 1:
        return "Alice"
    return None


# Literal: 限定具体取值
Mode = Literal["read", "write", "append"]


def open_resource(mode: Mode) -> None:
    print(f"打开模式：{mode}")


# open_resource("write")
