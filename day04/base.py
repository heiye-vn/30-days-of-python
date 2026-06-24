"""
字符串（String）
"""

"""
===== 1. 字符串创建方式 =====
"""
# 单引号/双引号，没什么区别，主要是方便内部嵌套引号
str1 = 'Hello, Python!'
str2 = "It's a beautiful day."
# print("This is 'Python' doc")

# 三引号用于多行字符串
str3 = """这是一个
多行字符串
非常适合写长文本。"""
# print(str3)

# 使用 str() 构造函数
str4 = str('this is python')
# print(str4)
# print(True)


"""
===== 2. 字符串的不可变性（Immutability） =====
字符串一旦被创建，其内容就不能被修改。如果修改字符串中的某个字符, 会报错。
所有的字符串修改操作，实际上都是在内存中创建了一个新的字符串。
"""
text = "Python"
# text[0] = 'p' # TypeError: 'str' object does not support item assignment

# 正确做法
# text = "p" + text[1:]
text = text.replace('P', 'p')
# print(text)


"""
===== 3. 字符串的运算 =====
"""
first = 'Hello'
second = 'Python'
# print(first + ' ' + second)  # 拼接字符串
# print("-".join(['a', 'b', 'c']))
# print(first * 3)  # 重复字符串


"""
===== 4. 索引和切片(Indexing and Slicing) =====
"""
# 索引：正向索引（从 0 开始）、反向索引（从 -1 开始）
s = "PythonString"
# print(s[0])
# print(s[-3])

# 切片：[start:stop:step]（包含 start（默认0），不包含 stop（默认 len - 1）），step 步长（默认 +1 ）
# print(s[0:6])
# print(s[6:])
# print(s[:6])
# print(s[-1:-4:-1])  # 'gni'
# print(s[-3:])  # 'ing'
# print(s[::2])  # (每隔一个取)
# print(s[::-1])  # 经典反转字符串，倒序


"""
===== 5. 字符串格式化（Formatting）=====
"""
name = "Alice"
age = 25
pi = 3.14159265

# 1. f-string (推荐使用)
# print(f"My name is {name} and I am {age} years old.")
# print(f"{1000000:_}")  # 1,000,000
# 表达式计算
# print(f"{age * 2 = }")
# print(f"age * 2 = {age * 2}")
# print(f"{len('hello') > 3}")  # 'True'
# 格式规范 mini-language
# print(f"{pi:.2f}")  # 保留两位小数
# print(f"{1234567:,}")  # 千分位逗号
# print(f"{0.75:.2%}")  # 百分比
# print(f"{'hi':>10}")  # 右对齐，宽度 10
# print(f"{'hi':*^10}")  # 居中填充
# 日期格式化
from datetime import datetime

now = datetime.now()
""" 常见的时间格式码
小写类：
%y：两位数的年份，26
%m：两位数的月份（01-12）
%d：两位数的日期
%b：月份的简写（Oct）
%a：星期的几的简写（Fri）
%h：和 %b 相同
%p：上午/下午（AM/PM）

大写类：
%Y：四位数的年份，2026
%M：两位数的分钟（00-59）
%B：月份的全称（October）
%A：星期几的全称（Friday）
%H：24 小时制（00-23）
%I：12 小时制（01-12）
%S：秒（00-59）
"""
# print(f"{now:%Y-%m-%d %H:%M:%S}")
# print(f"完整格式: {now:%A, %B %d, %Y}")

# 2. format() 方法 (兼容性好)
# print("My name is {} and I am {} years old.".format(name, age))
# print("姓名：{name}，年龄：{age}".format(name="Tom", age=20))  # 命名参数
# print("{:.2f}".format(3.14159))
# print("{:>10}".format("right"))
# print("{:,}".format(1000000))  # [ :, ] 千分位固定语法格式
# print("{0} {1} {0} {1}".format("hello", "world"))

# 3. % 格式化 (老式写法，类似于 C 语言，不推荐新代码使用)
# print("My name is %s, and I am %d years old." % (name, age))


"""
===== 6. 编码与解码（Bytes vs Str）=====
字符串和字节之间可以相互转换
"""
# str → bytes (编码)
textStr = "你好世界"
encoded = textStr.encode("utf-8")
# print(encoded)
# print(type(encoded))

# bytes → str (解码)
decoded = encoded.decode("utf-8")
# print(decoded)

# 文件读写时注意编码
# with open("data.txt", "r", encoding="utf-8") as f:
#     content = f.read()
#     print(content)


"""
===== 7. 转义字符与原始字符串（Raw String）
"""
# print("Hello\nWorld")  # [ \n ] 换行符
# print('Days\tTopics\tExercises')  # [ \t ] 制表符
# print('Day 1\t5\t5')
# print('Day 2\t6\t20')
# print('Day 3\t5\t23')
# print('Day 4\t1\t35')
# print('This is a backslash  symbol (Y\\n) Y')  # [ \\ ] 反斜杠
# print("This is \"Python\"")  # [ \" ] 双引号（可以不用转义符，需搭配单引号）
# print('This is \'Python\'')  # [ \' ] 单引号（可以不用转义符，需搭配双引号）
# print("\r world")  # [ \r ] 回车符

# 原始字符串（Raw String），一般用于处理文件路径，正则表达式
path = r"C:\Users\Admin\test.txt"
# print(path)
regex = r"\d+\.\d+"
# print(regex)

normal = "C:\\Users\\name\\file.txt"  # 需要使用 [ \\ ] 双反斜杠转义
# print(normal)


"""
===== 8. 字符串比较
字符串可以直接比较，按 Unicode 编码顺序逐字符比较
比较时会从左到右逐个字符进行，一旦出现不同字符，就根据其编码值决定大小；如果前缀相同，则较长的字符串更大
"""
# print("abc" == "abc")
# print("abc" != "ABC")
# print("apple" < "banana")
# print("abc" > "ab")
