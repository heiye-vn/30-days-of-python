# 常用内置函数


#  ===== 1. 输入输出 =====
# print("Hello")
# print(1, 2, 3)
# print("name", "Tom", sep="-")
# print("Hello", end="")

# name = input("请输入姓名：")
# print(name)


# ===== 2. 类型转换 =====
# a = int("100")
# print(a)
# print(type(a))

# b = float("3.14")
# print(b)
# print(type(b))

# age = 18
# print(str(age))
# print(type(str(age)))

# print(bool(1))
# print(bool(0))
# print(bool(""))
# print(bool("abc"))

# s = "abc"
# print(list(s))

# print(tuple([1,2,3]))

# print(set([1,2,2,3]))

# data = [
#     ("name","Tom"),
#     ("age",18)
# ]
# print(dict(data))


# ===== 3. 数学函数 =====
# print(abs(-100)) # 绝对值

# print(round(3.14159,2)) # 四舍五入

# print(max(3,8,5))

# print(min(3,8,5))

# nums=[1,2,3]
# print(sum(nums))

# print(pow(2,5, 7))

# print(divmod(10,3)) # 同时返回商和余数 (3, 1)


# ===== 4. 序列函数 =====
# print(len("hello"))

# nums = [5, 2, 8, 1]
# print(sorted(nums, reverse=True))  # 返回新的排序结果，默认升序，设置 reverse = True 则为降序

# nums=[1,2,3]
# print(list(reversed(nums))) # 返回新的反转结果

# fruits=["苹果","香蕉","橘子"]
# for index,item in enumerate(fruits):    # enumerate 返回一个枚举对象
#     print(index,item)

# names=["Tom","Jack"]
# ages=[18,20]
# print(list(zip(names,ages))) # zip() 将多个可迭代对象组合成一个元组格式的迭代器对象

# range() 作用是生成一个整数序列，通常用于循环计数
# 1. range(stop) - 从 0 开始，到 stop-1 结束
# for i in range(5):
#     print(i)

# 2. range(start, stop) - 从 start 开始，到 stop-1 结束
# for i in range(0, 10, 2):
#     print(i)

# 2. range(start, stop) - 从 start 开始，到 stop-1 结束
# for i in range(2, 6):
#     print(i)

# 3. range(start, stop, step) - 指定步长
# for i in range(0, 10, 2):
#     print(i)

# range() 常见使用场景
# I: 按索引遍历列表
# fruits = ["苹果", "香蕉", "橘子"]
# for i in range(len(fruits)):
#     print(f"第 {i+1} 个水果是 {fruits[i]}")

# II: 重复执行某操作 N 次
# for i in range(3):
#     print("Hello!")

# III: 倒序循环
# for i in range(5, 0, -1):
#     print(i)

# IV: 创建数字列表
# even_nums = list(range(0, 10, 2))
# print(even_nums)


# ===== 5. 判断函数 =====
# print(isinstance(10,int)) # 检查对象是否是指定类型（或类型元组中的某个类型）的实例
# print(isinstance('abc', (str, tuple)))

# print(type("abc"))

# a=[]
# print(id(a)) # id() 用于返回对象的唯一标识符（内存地址）

# print(hash("hello")) # hash() 返回对象的哈希值
# print(hash(42)) # 整数的 hash 是值本身
# print(hash(3.14))
# print(hash(True))
# print(hash(False))

# print(callable(20)) # callable() 判断对象是否可以调用
# print(callable(print))


"""
===== 6. 迭代器相关 =====
iter() 和 next() 是搭配使用的
1. iter() - 创建迭代器对象
2. next() - 从迭代器中获取下一个元素
"""
# nums=[1,2,3]
# it=iter(nums)
# print(next(it))

# it = iter([1, 2])
# print(next(it))
# print(next(it))
# print(next(it, '没有值了'))
# print(next(it,None)) # 提供默认值，避免 StopIteration 异常

# fruits = ["苹果", "香蕉", "橘子"]
# it = iter(fruits)
# while True:
#     try:
#         item = next(it)
#         print(item)
#     except StopIteration:
#         print("迭代结束")
#         break


# ===== 7. 高阶函数 =====
# nums=[1,2,3]
# result=map(lambda x:x*2,nums)
# print(list(result))
# print(list(result)) # map() 函数返回一个迭代器对象，因此不能重复使用
#
# nums=[1,2,3,4]
# result=filter(lambda x:x%2==0,nums)
# print(list(result))
# print(list(result)) # filter() 函数返回一个迭代器对象，因此不能重复使用

# nums=[0,0,1]
# print(any(nums)) # any() 用于判断可迭代对象中是否至少有一个元素为真值（True）
# print(any("hello"))

# nums=[1,2,0]
# print(all(nums)) # all() 用于判断可迭代对象中是否所有元素均为真值（True）


# ===== 8. 对象相关 =====
# class User:
#     name = "Tom"
#     age = 18
#
#     def __str__(self):
#         return f"User ｛ name: {self.name}, age: {self.age} ｝"
#
#
# u = User()
# print(getattr(u, "name"))  # getattr() 返回对象中指定名称的属性值

# setattr(u, "age", 20) # setattr() 设置对象中指定名称的属性值，没有则创建
# print(u.age)

# print(hasattr(u,"name")) # hasattr() 检查对象中是否有指定名称的属性

# print(f"用户: {u}")
# delattr(u,"name") # delattr() 删除对象中指定名称的属性


# ===== 9. 进制转换 =====
# print(bin(10)) # bin() 函数将整数转换成二进制字符串
#
# print(oct(10)) # oct() 函数将整数转换成八进制字符串
#
# print(hex(255)) # hex() 函数将整数转换成十六进制字符串


# ===== 10. 字符处理 =====
# print(chr(65)) # chr() 函数将 ASCII 码转换成字符

# print(ord("A")) # ord() 函数将字符转换成 ASCII 码


# ===== 11. 格式化 =====
"""
.2f
│ │ │
│ │ └─ f = float（浮点数）
│ └─── 2 = 保留 2 位小数
└───── . = 小数点分隔符
"""
# print(format(3.1415926,".2f")) # format() 函数将 value 转换为格式化后的形式


# ===== 12. 调试 =====
# print(dir(str)) # dir() 查看对象有哪些属性/方法

# help(list) # help() 显示对象属性/方法的帮助信息


# ===== 13. 文件操作 =====
with open("test.txt", "w") as f:
    f.write("Hello")

with open("test.txt", "r") as f:
    print(f.read())

# ===== 14. 执行代码 =====
print(eval("1+2"))

code = """
for i in range(3):
    print(i)
"""
exec(code)
