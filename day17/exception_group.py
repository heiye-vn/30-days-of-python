"""
Python 3.11 引入了 ExceptionGroup，用于同时处理多个异常，这在并发编程中特别有用

语法：
ExceptionGroup
exception*
"""


def validate_user(data):
    errors = []

    if not data.get("name"):
        errors.append(ValueError("姓名不能为空"))
    if not data.get("email"):
        errors.append(ValueError("邮箱不能为空"))
    if data.get("age", 0) < 0:
        errors.append((ValueError("年龄不能为负数")))

    if errors:
        raise ExceptionGroup("用户数据校验失败", errors)


try:
    validate_user({"name": "", "email": "", "age": -1})
except* ValueError as eg:
    for err in eg.exceptions:
        print(f"校验错误：{err}")
