"""
在实际开发中，循环是使用最频繁但也最容易埋下 Bug 的地方。
以下是结合实际应用场景总结的 5 大核心注意事项
"""

"""
1. 警惕死循环，必须设置“安全阀门”
    - 问题表现：使用 while 循环时，由于漏写了条件更新代码，或者跳出条件永远无法满足，导致 CPU 占用率飙升到 100%，程序卡死
    - 实际场景：网络请求重试机制。当向服务器请求数据失败时，我们希望循环重试，但如果服务器彻底宕机，不加限制的重试就会变成死循环
"""
# 设置最大重试次数
# max_retries = 3
# attempts = 0
# success = False
# while attempts < max_retries:
#     attempts += 1
#     if connect_server():
#         success = True
#         break
#     print(f"连接失败，正在进行第 {attempts} 次重试...")f
#     print("达到最大重试次数，放弃连接并报警！")


"""
2. 绝对不要在遍历列表的同时修改该列表
    - 问题表现：在 for 循环遍历一个列表时，在循环体内部对该列表进行 remove() 或 append() 操作，这会导致列表的内存索引立刻发生错乱，从而漏掉部分元素或导致死循环
    - 实际场景：清理购物车/注销过期用户。遍历用户列表，删除其中已经注销的用户。
"""
# 错误的做法：直接删除
# invalid_users = ["user1", "user2", "user3"]  # 假设 list 很大
# for user in invalid_users:
#     if is_inactive(user):
#         invalid_users.remove(user)  # 索引移动，user3 会被跳过

# 正确的做法：遍历原列表的副本 [:]
# for user in invalid_users[:]:
#     if is_inactive(user):
#         invalid_users.remove(user)

# 或者使用列表推导式（更 Pythonic）
# valid_users = [user for user in all_users if not is_inactive(user)]


"""
3. 避免过深的嵌套循环，小心性能爆炸
    - 问题表现：双层嵌套循环的时间复杂度是 O(N^2)。如果外层有 1 万条数据，内层也有 1 万条数据，循环体就会执行 1 亿次，程序会变得极慢
    - 实际场景：数据匹配。有 1 万个学生数据和 1 万个成绩数据，需要把成绩匹配给对应的学生
"""
# 错误做法（使用嵌套双循环，极慢）
# for student in students:  # 循环 10000 次
#     for score in scores:  # 循环 10000 次
#         if student["id"] == score["student_id"]:
#             student["score"] = score["grade"]
#             break

# 正确做法（用字典/哈希表将复杂度降到 O(N)）
# 先把成绩转为字典，查询复杂度降为 O(1)
# score_dict = {score["student_id"]: score["grade"] for score in scores}
# # 只需要一层循环即可完成匹配
# for student in students:
#     student["score"] = score_dict.get(student["id"], 0)


"""
4. 循环内部要及时释放资源，避免资源泄露
    - 问题表现：在循环内部打开文件、数据库连接、网络套接字(Socket)时，如果没有及时关闭，随着循环次数增加，系统资源会被耗尽（报 Too many open files 错误）
    - 实际场景：处理大量 Excel 文件上传。一个 Excel 文件本质上就是一个压缩包，打开它会占用系统内存和 CPU。
"""
# 错误示范
# for file_path in log_files:
#     f = open(file_path, "r")  # 打开了文件但没有关闭，资源持续被占用
#     process_data(f.read())

# 正确示范（使用 with 语句确保每次循环结束自动关闭文件）
# for file_path in log_files:
#     with open(file_path, "r") as f:
#         process_data(f.read())  # 离开 with 代码块时，文件会被安全关闭


"""
5. 优先使用 Python 风格(Pythonic)的替代方案
    - 问题表现：习惯了 C/Java 语法的开发者，喜欢用 range(len(list)) 来遍历列表取值，或者用繁琐的循环来做简单的数据过滤，这在 Python 中是不够优雅且效率较低的
    - 实际场景：过滤并求平方。将列表中的偶数挑选出来并平方
"""
# 错误是否（传统方式）
# numbers = [1, 2, 3, 4, 5]
# results = []
# for i in range(len(numbers)):  # ❌ 尽量避免使用 range(len(...))
#     if numbers[i] % 2 == 0:
#         results.append(numbers[i] ** 2)


# 正确做法（列表推导式，更 Pythonic）
# numbers = [1, 2, 3, 4, 5]
# # 一行搞定，底层经过了 C 语言级别的优化，速度更快
# results = [num**2 for num in numbers if num % 2 == 0]
# print(f"results: {results}")


"""
| 建议       | 推荐做法                               |
| -------- | ---------------------------------- |
| 遍历集合     | 优先使用 `for`，避免不必要的 `while`          |
| 获取索引     | 使用 `enumerate()`，不要手动维护计数器         |
| 同时遍历多个序列 | 使用 `zip()`                         |
| 查找数据     | 优先使用 `set` 或 `dict` 降低时间复杂度        |
| 修改列表     | 不要遍历原列表进行增删，遍历副本或创建新列表             |
| 数据库/网络   | 避免在循环中逐条操作，尽量批量处理或并发处理             |
| 性能       | 避免在循环中重复执行耗时计算、频繁创建对象或大量 `print()` |
| 可维护性     | 避免过深的嵌套循环，必要时拆分函数                  |
| 容错       | 批量任务中适当捕获异常，避免一条数据出错导致整个循环终止       |
| 可读性      | 推导式适合简单场景，复杂逻辑优先使用普通 `for` 循环      |

"""
