"""
Python 中函数参数定义必须遵循严格的顺序

def complete_function(
    pos_only,            # 1. 位置参数（仅位置）
    /,                   #    位置参数分隔符（Python 3.8+）
    normal,              # 2. 普通位置/关键字参数
    *args,               # 3. 可变位置参数（打包）
    keyword_only,        # 4. 仅关键字参数
    *,                   #    仅关键字分隔符（当不需要 *args 时使用）
    **kwargs             # 5. 可变关键字参数（打包）
):
    pass

"""


def register_user(
        username, /, password, *roles, email=None, department="general", **metadata
):
    user = {
        "username": username,
        "password": password,
        "roles": roles,
        "email": email,
        "department": department,
        "metadata": metadata,
    }
    return user


# 所有位置参数必须放在关键字参数之前
new_user = register_user(
    "alice",
    "secret123",  # password 可以以关键字参数传递，但是这里后面有位置参数，故只能以位置参数传递
    "admin",
    "editor",  # roles（*args，可变位置参数）
    email="alice@example.comn",  # email（关键字参数）
    department="tech",  # department（关键字参数）
    phone="138800138000",  # metadata（可变关键字参数）
    location="Beijing",  # metadata（可变关键字参数）
)
print(new_user)

"""
函数形参中的 " / " 是一个仅位置参数的分隔符，在 / 之前的参数只能是位置参数，在 / 之后的参数可以是位置参数或关键字参数
"""


def test_func1(a, /, b, c):
    print(a, b, c)


# 错误调用
# test_func1(a=1, b=2, c=3) # TypeError: test_func1() got some positional-only arguments passed as keyword arguments: 'a'

# 正确调用
# test_func1(1, b=2, c=3)


"""
函数形参中的单个 " * " 是一个仅关键字参数的分隔符，在 * 之后的参数只能是关键字参数，在 * 之前的参数可以是位置参数或关键字参数
"""


def configure_system(ip, port, *, timeout=30, debug=False):
    print(ip, port, timeout, debug)

# 错误调用
# configure_system("192.168.1.1", 8080, 10, True) # configure_system() takes 2 positional arguments but 4 were given

# 正确调用
# configure_system("192.168.1.1", 8080, timeout=10, debug=True)
