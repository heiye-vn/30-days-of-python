"""
异常处理（Exception Handing）
"""

# from venv import logger

"""
try...except 语法
把可能出错的代码放在 try 块中，把错误处理逻辑放在 except 块中
核心本质是确保程序的健壮性
"""

# try:
#     result = 10 / 0
# except ZeroDivisionError:
#     print("错误：被除数不能为零！")
#     result = 0
#
# print(f"结果是：{result}")


"""
捕获多种异常
"""


def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        print("错误：被除数不能为零！")
        return None
    except TypeError:
        print("错误：参数必须是数字！")
        return None


# print(safe_divide(10, 2))
# print(safe_divide(10, 0))
# print(safe_divide("22", 2))  # noqa


"""
捕获异常对象
在 except 块中，可以使用 as 关键字将异常对象赋值给一个变量，然后通过这个变量来访问异常对象的属性和方法，从而访问更详细的错误信息
例如，可以通过异常对象的 args 属性来访问异常对象的参数，是一个元组，包含异常对象的参数
"""
# try:
#     data = {"name": "Alice"}
#     print(data["age"])
# except KeyError as e:
#     print(f"缺失的键是：{e}")
#     print(f"异常类型是：{type(e)}")
#     print(f"异常参数是：{e.args}")  # ("age",)


"""
用一个 except 捕获多种异常
"""
# try:
#     value = int("hello")
# except (ValueError, TypeError) as e:
#     print(f"转换失败：{e}")


"""
异常处理流程的完整结构：try...except...else...finally

try:
    # 可能出错的代码
    ...
except SomeError:
    # 出错时执行
    ...
else:
    # 没出错时执行（try 块成功时）
    ...
finally:
    # 无论如何都会执行（清理资源）
    ...
"""

"""
raise 主动抛出异常
可以使用 raise 关键字主动抛出异常，从而触发异常处理流程
"""


def set_age(age):
    if not isinstance(age, int):
        raise TypeError(f"年龄必须是整数：{age}")
    if age < 0 or age > 150:
        raise ValueError(f"年龄{age}不在合理范围内（0-150）")
    return age


# try:
#     set_age(5.2)
# except (TypeError, ValueError) as e:
#     print(e)


"""
raise...from 异常链
当捕获一个异常后抛出另一个异常时，可以使用 form 保留原始异常的上下文
"""


class DatabaseConnectionError(Exception):
    """自定义数据库连接异常"""
    pass


def connect_db(host, port):
    try:
        # 模拟底层网络异常
        raise ConnectionRefusedError(f"无法连接到 {host}:{port}")
    except ConnectionRefusedError as e:
        raise DatabaseConnectionError("数据库服务不可用") from e


# try:
#     connect_db("localhost", 5432)
# except DatabaseConnectionError as e:
#     print(f"应用层异常: {e}")
#     print(f"根因异常: {e.__cause__}")


"""
异常处理的最佳实践
"""

# 1. 尽量精准捕获，避免裸 except
# ❌ 不推荐：会吞掉所有异常，包括 KeyboardInterrupt 和 SystemExit
# try:
#     ...
# except:  # noqa
#     pass

# ❌ 也不推荐使用 Exception：范围太广
# try:
#     ...
# except Exception:
#     pass

# ✅ 推荐：精确捕获预期的异常
# try:
#     ...
# except (TypeError, ValueError, KeyError) as e:
#     logger.error(f"数据处理失败：{e}")


# 2. 记录异常信息
# import logging
#
# logger = logging.getLogger(__name__)
#
# try:
#     result = risky_operation() # noqa
# except SpecialFileError as e:
#     logger.exception("操作失败，详细信息如下") # exception() 会自动记录堆栈
#     raise # 记录后继续向上抛出


"""
3. EAFP vs LBYL

LBYL（Look Before You Leap）- 先检查再操作

if key in dictionary:
    value = dictionary[key]
else:
    value = default_value
    
EAFP（Easier to Ask Forgiveness than Permission）- Pythonic 风格

try:
    value = dictionary[key]
except KeyError:
    value = default_value

更简洁的代替方案
value = dictionary.get(key, default_value)
"""


# 4. 不要忽略 finally 中的异常风险
# ❌ finally 中的 return 会吞掉 except 中的异常
def bad_function():
    try:
        raise ValueError("重要错误")
    except ValueError:
        print("捕获到异常")
    finally:
        return "这会吞掉异常"


# bad_function()

# ✅ 在 finally 中只做清理工作
def good_function():
    try:
        raise ValueError("重要错误")
    except ValueError:
        print("捕获到异常")
        raise  # 让异常继续传播
    finally:
        print("清理资源")

# good_function()
