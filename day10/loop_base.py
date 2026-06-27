"""
Python 中的循环是编程中最核心的控制流结构之一，主要用于重复执行代码块。
Python 提供了两种主要的循环结构: for 循环和 while 循环，以及一系列用于控制循环行为的关键词和内置函数
💡: Python 中, 一般for 循环的使用优先级高于 while 循环

控制关键字：
- break:立即结束循环
- continue: 跳过本次循环，进入下一次循环
- pass: 占位符，防止报错
- else: 循环正常结束才执行，如果是 (break / return / 抛出异常) 等非正常结束的循环，则不会执行

辅助函数：
- range(start, stop, step): 数字范围循环
- enumerate(): 遍历时同时获取索引和值
- zip(): 多个列表一起遍历，会以最短地可迭代对象为准

其他用法：
- 嵌套循环: 循环内部再进行循环
- 推导式（列表推导式等）
"""

"""
===== 1 for 循环（知道要遍历什么） =====
for 循环用于遍历任何可迭代对象（列表、元组、字符串、字典、集合等）
"""


"""
===== 2. while 循环（不知道循环多少次）=====
当循环次数不确定，需要根据条件判断是否继续时使用（比如等待网络连接、等待用户输入特定指令等）

💡：别忘了更新条件，否则会死循环
"""
# count = 0
# while count < 5:
#     print(count)
#     count += 1  # ⚠️ 别忘了更新条件，否则会死循环


# while True:
#     password = input("请输入密码: ")
#     if password == "admin123":
#         print("登录成功!")
#         break
#     print("密码错误，请重试")


"""
===== 3. 辅助函数用法 =====
"""
# 用法一：range(stop)：0 到 stop-1
# for i in range(5):
#     print(i)

# 用法二：range(start, stop, step)：start 到 stop-1，步长为 step
# for i in range(1, 11, 2):
#     print(f"奇数: {i}")

# 用法三：倒序
# for i in range(5, 0, -1):
#     print(i, end=" ")


# enumerate() 使用示例
# names = ["小明", "小红", "小刚"]
# # start = 1 设置生成的索引从 1 开始计数，但实际索引是从 0 开始
# for index, name in enumerate(names, start=1):
#     print(f"第 {index} 名是: {name}")


# zip() 使用示例
# names = ["Alice", "Bob", "Carol"]
# scores = [90, 85, 92]
# for name, score in zip(names, scores):
#     print(f"{name}: {score}分")


# 当迭代对象长度不一致时，zip() 会以最短的可迭代对象为准
# a = [1, 2]
# b = ["A", "B", "C"]
# for x, y in zip(a, b):
#     print(x, y)


"""
===== 4. 控制语句 =====
"""
# continue 跳过本次循环，进入下一次循环
# for i in range(6):
#     if i == 3:
#         continue  # 跳过 3
#     print(i)


# pass 占位符，防止报错，不执行任何操作
# for i in range(5):
#     pass

# for...else 只有循环正常结束才执行 else
# for i in range(5):
#     print(i)
# else:
#     print("循环正常结束了！")

# 使用 break 终止循环
# num = 2
# while num < 5:
#     if num == 3:
#         print("遇到 3, 执行 break 终止循环！")
#         break
#     print(num)
#     num += 1
# else:
#     print("循环正常结束了！")  # 不会执行该语句

# break 终止循环
# while True:
#     user_input = input("输入 q 退出：")
#     if user_input == "q":
#         break
#     print(f"你输入了：{user_input}")

"""
===== 5. 嵌套循环 =====
循环内再套循环，常用于处理二维数据（矩阵、表格）
💡: 外层 break 只能退出内存循环，退出多层嵌套可以用标志变量或封装成函数
"""
# for i in range(3):
#     for j in range(2):
#         print(i, j)

# found = False
# for i in range(5):
#     for j in range(5):
#         if i * j > 6:
#             found = True
#             break
#     if found:
#         break
# print(f"i={i}, j={j}")  # noqa


# 九九乘法表
# for i in range(1, 10):
#     for j in range(1, i + 1):
#         print(f"{j} * {i} = {i * j}", end="\t")
#     print()  # 换行

# 打印星号三角形
# for i in range(5):
#     for j in range(i + 1):
#         print("*", end=" ")
#     print()

# 打印等腰三角形
# for i in range(5):
#     for j in range(5 - i):
#         print(" ", end=" ")
#     for k in range(2 * i + 1):
#         print("*", end=" ")
#     print()

# 打印实心菱形
# n = 5
# for i in range(n):
#     for j in range(n - i - 1):
#         print(" ", end=" ")
#     for k in range(2 * i + 1):
#         print("*", end=" ")
#     print()
# for i in range(n - 1, 0, -1):
#     for j in range(n - i):
#         print(" ", end=" ")
#     for k in range(2 * i - 1):
#         print("*", end=" ")
#     print()

# 打印空心菱形
n = 5
for i in range(n):
    for j in range(n - i - 1):
        print(" ", end=" ")
    for k in range(2 * i + 1):
        if k == 0 or k == 2 * i:
            print("*", end=" ")
        else:
            print(" ", end=" ")
    print()
for i in range(n - 1, 0, -1):
    for j in range(n - i):
        print(" ", end=" ")
    for k in range(2 * i - 1):
        if k == 0 or k == 2 * i - 2:
            print("*", end=" ")
        else:
            print(" ", end=" ")
    print()
