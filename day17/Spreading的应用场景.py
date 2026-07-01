"""
展开的应用场景
"""

from functools import partial, wraps
from itertools import chain

"""
场景一：构建灵活的函数装饰器
"""


def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}({args}, {kwargs})")
        result = func(*args, **kwargs)
        print(f"返回： {result}")
        return result

    return wrapper


@log_call
def calculate(a, b, operation="add"):
    if operation == "add":
        return a + b
    elif operation == "multiply":
        return a * b
    return None


# calculate(3, 5)
# calculate(3, 5, operation="multiply")


"""
场景二：partial 函数与参数展开

partial 作用：偏函数应用，允许通过“提前固定”一个函数的部分参数（Arguments），从而生成一个新的、参数更少的新函数
"""


def send_mail(to, subject, body, cc=None, bcc=None):
    print(f"发送邮件给：{to}")
    print(f"主题：{subject}")
    print(f"正文：{body}")
    if cc:
        print(f"抄送： {cc}")


# 创建一个预设参数的偏函数（固定一些不变参数）
send_weekly_report = partial(
    send_mail,
    to="team@example.com",
    subject="周报",
    cc="manager@example.com",
)

# 只需传入剩余参数（或者叫可变参数）
# send_weekly_report(body="本周完成了异常处理模块的编写...")


"""
场景三：数据管道中的解包与重组
"""


def process_student(stu_record):
    """处理学生纪律：解包 → 计算 → 重组"""
    name, *scores, student_id = stu_record
    avg_score = sum(scores) / len(scores)  # noqa
    max_score = max(scores)
    min_score = min(scores)

    return {
        "name": name,
        "student_id": student_id,
        "scores": scores,
        "stats": {
            "average": round(avg_score, 2),
            "max": max_score,
            "min": min_score,
            "count": len(scores),
        },
    }


# 批量处理
records = [
    ("Alice", 92, 88, 95, 78, "S001"),
    ("Bob", 67, 72, 80, 75, "S002"),
    ("Charlie", 95, 98, 92, 96, "S003"),
]

# for record in records:
#     cal_result = process_student(record)
#     print(
#         f"{cal_result['name']}({cal_result['student_id']}): "
#         f"平均分 {cal_result['stats']['average']}, "  # noqa
#         f"最高分 {cal_result['stats']['max']}, "  # noqa
#         f"最低分 {cal_result['stats']['min']}"  # noqa
#     )


"""
场景四：列表展平（Flatten）
"""
# 嵌套列表展平
nested = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
flat = [*nested[0], *nested[1], *nested[2]]
print(flat)


# 更通用的展平方法
def flatten(lists):
    return [item for child_list in lists for item in child_list]


print(flatten(nested))

# 使用 itertools.chain（最高效）
flat_ = list(chain.from_iterable(nested))
print(flat_)
