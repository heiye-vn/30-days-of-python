"""
Python 中的条件语句是控制程序流程的核心工具，它允许程序根据不同的条件执行不同的代码块。
Python 的条件语句主要包括 if、elif、else，以及三元表达式和模式匹配
"""

"""
===== 基础语法：if / elif /else =====
使用缩进（通常为 4 个空格）来定义代码块，而不是大括号 ｛｝
elif 可以有任意多个，else 最多一个且必须在最后。执行逻辑是从上往下依次判断
嵌套 if 语句，即在一个 if 语句内部再嵌套另一个 if 语句，避免过多嵌套，以免代码难以阅读和维护
"""
# score = 85
# if score >= 90:
#     print("优秀！拿到了 A")
# elif score >= 80:
#     print("良好！拿到了 B")
# elif score >= 60:
#     print("及格！拿到了 C")
# else:
#     print("不及格，下次加把劲！")

# is_holiday = True  # 是否是节假日
# age = 14  # 年龄
# if is_holiday:
#     print("节假日期间无打折")
#     if age < 14:
#         print("儿童票：半价")
#     else:
#         print("成人票：原价")
# else:
#     print("工作日期间：全场 8 折！")

"""
结合运算符使用
为了提升间接性和多层判断，可结合各种运算符

比较运算符：==、!=、>、<、>=、<=
逻辑运算符：and、or、not
成员运算符：in、not in
身份运算符：is、is not

💡：== 比较的是值，is 比较的是内存地址
"""
# print({"a": 111} is not {"b": 222})

# age = 22
# money = 300
# student = False
# if age >= 18 and (money >= 200 or student):
#     print("可以买")

# vip = False
# if not vip:
#     print("普通用户")

# 使用运算符改写上面判断
# if not is_holiday:
#     print("工作日期间：全场 8 折！")
# elif age < 14:
#     print("节假日期间无打折")
#     print("儿童票：半价")
# else:
#     print("节假日期间无打折")
#     print("成人票：原价")


"""
===== 三元运算符 =====
语法：变量 = 值1 if 条件 else 值2
"""
# age = 20
#
# status = "成年" if age >= 18 else "未成年"
# print(status)


"""
match...case：结构化模式匹配，类似 switch...case
_ 表示默认分支，相当于 else / default
"""
# status = 404
# match status:
#     case 200:
#         print("请求成功")
#     case 404:
#         print("资源不存在")
#     case 500:
#         print("服务器错误")
#     case _:
#         print("未知状态")

# 匹配多个 case 使用 [ | ]
# day = "Sat"
# match day:
#     case "Sat" | "Sun":
#         print("周末")
#     case _:
#         print("工作日")

# 结构序列
# point = (3, 5)
# match point:
#     case (0, 0):
#         print("原点")
#     case (x, 0):
#         print(f"X轴上的点：{x}")
#     case (0, y):
#         print(f"Y轴上的点：{y}")
#     case (x, y):
#         print(f"普通点：({x}, {y})")

# 结合 if
point = (3, -5)
match point:
    case (x, y) if x > 0 and y > 0:
        print(f"点({x},{y})在第一象限")
    case (x, y) if x < 0 < y:
        print(f"点({x},{y})在第二象限")
    case (x, y) if x < 0 and y < 0:
        print(f"点({x},{y})在第三象限")
    case (x, y) if x > 0 > y:
        print(f"点({x},{y})在第四象限")
    case (0, 0):
        print("原点")
    case (_, 0):
        print("X轴上的点")
    case (0, _):
        print("Y轴上的点")
    case _:
        print("未知点")
