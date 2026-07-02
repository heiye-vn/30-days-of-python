"""
正则的基本语法
"""

import re

"""
标志（Flags）
标志可以改变正则表达式的匹配行为，作为可选参数传入

re.I 或 re.IGNORECASE：忽略大小写
re.M 或 re.MULTILINE：多行模式
re.S 或 re.DOTALL：让点匹配所有字符
re.X 或 re.VERBOSE：允许在正则中学注释和空格，方便阅读
"""
# 忽略大小写
# print(re.findall(r"python", "Python PYTHON python", re.IGNORECASE))

# 多行模式
multi_text = """第一行 hello
第二行 hello
第三行 world"""

# 没有 MULTILINE，^ 只匹配字符串的开头
# print(re.findall(r"^第.*行", multi_text))
# 有 MULTILINE，^ 匹配每一行的开头
# print(re.findall(r"^第.*行", multi_text, re.MULTILINE))

# DOTALL 让 . 匹配所有字符
text_dot = "start\nmiddle\nend"
# print(re.findall(r"start.*end", text_dot, re.DOTALL))


"""
前瞻与后顾（断言）
断言用来指定"某个位置的前面或后面必须（或不能）是什么"，但断言本身不消耗字符。
语法：
(?=...) 正向前瞻 => 后面必须是 ...
(?!...) 负向前瞻 => 后面不能是 ...
(?<=...) 正向后顾 => 前面必须是 ...
(?<!...) 负向后顾 => 前面不能是 ...
"""
text = "python3 is great, python2 is old"

# 正向前瞻：匹配后面跟着数字的 "python"
# print(re.findall(r"python(?=\d)", text))

# 负向前瞻：匹配后面不跟 3 的 "python"
# print(re.findall(r"python(?!3)", text))

# 正向顾后：匹配前面是 "py" 的 "thon"
# print(re.findall(r"(?<=py)thon", text))

# 负向顾后：匹配前面不说 "java" 的 "script"
text2 = "javascript is popular, typescript too, but not javascript right"
print(re.findall(r"(?<!java)script", text2))
