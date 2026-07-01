"""
打包（Packing）：将多个值收集到一个容器中，使用 * 和 ** 运算符实现
"""

"""
*args
位置参数打包，将多余的位置参数打包成一个元组（tuple）
"""


def greet(*args):
    print(f"args 类型：{type(args)}")
    print(f"args 内容：{args}")
    for name in args:  # noqa
        print(f"你好，{name}！")


# greet("Alice")
# greet("Alice", "Bod", "Dived")


# 与固定参数混合使用
def log_event(event_type, *details):
    """第一个参数是事件类型，其余参数是事件详情"""
    print(f"事件类型：{event_type}")
    print(f"详情：{details}")


# log_event("ERROR", "数据库连接失败", "重试3次后放弃", "已通知管理员")


"""
*kwargs
关键字参数打包，将多余的关键字参数打包成一个字典（dict）
"""


def create_profile(**kwargs):
    print(f"kwargs 类型：{type(kwargs)}")
    print(f"kwargs 内容：{kwargs}")


# create_profile(name="Alice", age=30, city="Beijing")

# 与固定参数混合使用
def build_query(table, **conditions):
    """构建 SQL 查询条件"""
    where_clauses = [f"{col} = '{val}'" for col, val in conditions.items()]
    sql = f"SELECT * FROM {table}"
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)
    return sql


query = build_query("user", name="Alice", age=30, status="active")
# print(query)


"""
解包（Unpacking）：解包是打包的逆操作 ——  将容器中的元素拆分并赋值给多个变量
"""
# 基础解包（元组解包、列表解包、字符串解包、集合/字典解包【注意集合无序】）
# x, y, z = (1, 2, 3)
# print(x, y, z)

# a, b, c = [10, 20, 30]
# print(a, b, c)

# first, second, third = "ABC"
# print(first, second, third)

# m, n = {1, 2}
# print(m, n)

# k1, k2 = {"name": "张三", "age": 20}
# print(k1, k2)


"""
星号解包（* 捕获剩余元素）
返回的结果永远是一个列表（list）
"""
# 捕获末尾
# first, *rest = [1, 2, 3, 4, 5]
# print(first)
# print(rest)

# 捕获头部
# *init, last = (1, 2, 3, 4, 5, 6)
# print(init)
# print(last)

# 捕获中间
# first_k, *middle_k, last_k = {"name": "王麻子", "age": 20, "city": "赵国", "skills": ["修仙", "杀伐", "恋爱"]}
# print(first_k)
# print(middle_k)
# print(last_k)

# * 号变量可以为空
# first, *rest = [1]
# print(first)
# print(rest)


# 只取首尾（下划线 _ 是约定俗成的 “不关心” 变量名，不需要使用）
head, *_, tail = range(10)
# print(head)
# print(tail)

# 实际应用：处理 CSV 数据
csv_data = """name,email,phone,city,age
Alice,alice@mail.com,13800001111,Beijing,30
Bob,bob@mail.com,13900002222,Shanghai,25
Charlie,charlie@mail.com,13700003333,Shenzhen,28"""

# strip() 去除字符串两边的空白字符（空格，换行符，制表符），可指定字符
data_list = csv_data.strip().split("\n")
data_list = data_list[1:]  # 去除表头
for line in data_list:
    fields = line.split(",")
    name, email, *extras = fields
    print(f"{name}: {email}, 额外信息：{extras}")
