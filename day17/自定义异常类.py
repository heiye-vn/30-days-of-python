"""
在实际项目中，自定义异常能让错误语义更清晰、更贴合业务逻辑。

自定义异常类需要继承自 Exception 类或其子类，而非 BaseException 类。
"""


class AppError(Exception):
    """应用基础异常"""

    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


class ValidationError(AppError):
    """数据校验异常"""

    def __init__(self, field, message):
        super().__init__(f"字段 '{field}' 校验失败：{message}", code=400)
        self.field = field


class AuthenticationError(AppError):
    """认证异常"""

    def __init__(self, message="认证失败，请重新登录"):
        super().__init__(message, code=401)


class NotFoundError(AppError):
    """资源未找到异常"""

    def __init__(self, resource, resource_id):
        super().__init__(f"{resource}(ID={resource_id}) 不存在", code=404)
        self.resource = resource
        self.resource_id = resource_id


# 实际使用
def create_user(data):
    if not data.get("email"):
        raise ValidationError("email", "邮箱不能为空")
    if "@" not in data["email"]:
        raise ValidationError("email", "邮箱格式不正确")
    return {"id": 1, **data}


def get_user(user_id):
    users = {1: "Alice", 2: "Bob"}
    if user_id not in users:
        raise NotFoundError("用户", user_id)
    return users[user_id]


# 统一异常处理
def handle_request(action, **kwargs):
    try:
        if action == "create":
            return create_user(kwargs)
        elif action == 'get':
            return get_user(kwargs["user_id"])
    except ValidationError as e:
        print(f"[{e.code}] 校验错误 - {e}")
    except NotFoundError as e:
        print(f"[{e.code}] - 未找到 - {e}")
    except AuthenticationError as e:
        print(f"[{e.code}] - 认证错误 - {e}")
    except AppError as e:
        print(f"[{e.code}] 应用错误 - {e}")


# handle_request("create", email="")
# handle_request("create", email="invalid")
# handle_request("create", email="1064239893@qq.com")
handle_request("get", user_id=99)
