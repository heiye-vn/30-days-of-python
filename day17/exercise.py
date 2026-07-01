"""
Exercise
"""

"""
1. 异常处理练习
编写一个用户注册函数，校验邮箱格式、密码强度、年龄范围，对每种不合规情况抛出自定义异常，并在外层统一捕获处理
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


def user_register(user):
    email, password, age = user
    if not email:
        raise ValidationError("email", "邮箱不能为空")
    if "@" not in email:
        raise ValidationError("email", "邮箱格式不正确")
    if not password:
        raise ValidationError("password", "密码不能为空")
    if len(password) < 6:
        raise ValidationError("password", "密码长度不能少于6位")
    if not 18 <= age <= 100:
        raise ValidationError("age", "年龄必须在18到100之间")
    return {"email": email, "password": password, "age": age}


# try:
#     user_register(("example@example.com", "password123", 25))
# except ValidationError as e:
#     print(f"[{e.code}] {e}")
# else:
#     print("用户注册成功！")


"""
2. 打包练习
实现一个 multi_map(func, *iterables) 函数，对多个可迭代对象同时应用函数（类似内置的 map）
"""


def multi_map(func, *iterables):
    """自定义实现的 map 函数，支持惰性求值"""
    for args in zip(*iterables):
        yield func(*args)


# 测试 multi_map
# print("--- 练习 2 测试 ---")
add_three = lambda x, y, z: x + y + z  # noqa
list1 = [1, 2, 3]
list2 = [10, 20, 30, 40]
list3 = [100, 200, 300]
# mapped = multi_map(add_three, list1, list2, list3)
# print(list(mapped))


"""
3. 解包练习
给定一组 `(姓名, 成绩1, 成绩2, ..., 学号)` 格式的数据，用解包提取姓名和学号，用 `*` 捕获所有成绩
"""


def get_score(student_data):
    name, *scores, student_num = student_data
    print(f"姓名：{name}")
    print(f"学号：{student_num}")
    print(f"成绩：{scores}")


# get_score(("Alice", 91, 85, 60, 77, "S001"))


"""
4. 展开练习
实现一个函数合并多个字典，要求后面的字典中的列表值不是覆盖而是追加
"""


def merge_dicts(*dicts):
    result = {}
    for d in dicts:
        for key, value in d.items():
            if (
                key in result
                and isinstance(value, list)
                and isinstance(result[key], list)
            ):
                result[key].extend(value)
            else:
                # 若 value 为 list，存入其副本，防止污染原始字典
                result[key] = list(value) if isinstance(value, list) else value
    return result


# 测试合并字典
dict1 = {"a": [1, 2], "b": 3}
dict2 = {"a": [4, 5], "c": 6}
dict3 = {"b": 7, "d": [8, 9]}
# merged = merge_dicts(dict1, dict2, dict3)
# print(merged)


"""
5. 综合练习
构建一个简单的命令行工具，使用 *args 接收命令 and 参数，用异常处理捕获所有可能的错误并给出友好的提示
"""


def run_cli(*args):
    """简单命令行工具模拟，支持 add, div, greet 三种指令并包含完备的异常处理"""
    try:
        if not args:
            raise ValueError("未指定任何命令。请提供至少一个命令名称。")

        command = args[0]
        cmd_args = args[1:]

        if command == "add":
            if len(cmd_args) < 2:
                raise TypeError("加法指令 'add' 至少需要两个数值参数。")
            nums = [float(x) for x in cmd_args]
            result = sum(nums)
            print(f"[Success] {command} 执行结果: {result}")
            return result

        elif command == "div":
            if len(cmd_args) != 2:
                raise TypeError(
                    "除法指令 'div' 接收且仅接收两个数值参数（被除数 和 除数）。"
                )
            a, b = float(cmd_args[0]), float(cmd_args[1])
            result = a / b
            print(f"[Success] {command} 执行结果: {result}")
            return result

        elif command == "greet":
            if len(cmd_args) != 1:
                raise TypeError("问候指令 'greet' 接收且仅接收一个姓名参数。")
            name = cmd_args[0]
            print(f"[Success] {command} 执行结果: 你好，{name}！")
            return f"Hello, {name}!"

        else:
            raise NotImplementedError(
                f"未知指令 '{command}'。支持的指令: add, div, greet。"
            )

    except ValueError as e:
        print(f"[ValueError] 参数转换失败，请输入合法的数值。具体信息: {e}")
    except TypeError as e:
        print(f"[TypeError] 参数数量或类型不正确。具体信息: {e}")
    except ZeroDivisionError as e:
        print(f"[ZeroDivisionError] 除法运算中除数不能为零。具体信息: {e}")
    except NotImplementedError as e:
        print(f"[NotImplementedError] 指令不支持。具体信息: {e}")
    except Exception as e:
        print(f"[UnknownError] 发生意外错误。具体信息: {e}")


# 测试命令行工具
print("\n--- 练习 5 测试 ---")
run_cli()  # 触发缺少命令错误
run_cli("unknown_cmd")  # 触发未知指令错误
run_cli("add", "1.5", "2.5", "3")  # 正常相加
run_cli("add", "1", "abc")  # 触发数值转换错误
run_cli("div", "10", "2")  # 正常相除
run_cli("div", "10", "0")  # 触发除零错误
run_cli("greet", "张三")  # 正常问候
run_cli("greet")  # 触发参数个数错误
