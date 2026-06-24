""""
字符串常用方法
"""

"""
===== 1. 大小写转换与清理 =====
upper()：将所有字符转换为大写
lower()：将所有字符转换为小写
capitalize()：整个字符串的首字母大写
title()：将每个单词的首字母大写
swapcase()：大小写互换

lstrip()：清除左边空白
rstrip()：清除右边空白
strip()：清除两边空白
"""
s = "Hello World"
# print(s.upper())
# print(s.lower())
# print(s.capitalize())
# print('python is simple language'.title())
# print(s.swapcase())
# print("   abcdefg    ".lstrip())
# print("   abcdefg    ".rstrip())
# print("   abcdefg    ".strip())
# print("####hello####".strip('#'))  # 可以指定字符，不指定则默认删除空白字符


"""
===== 2. 字符串判断 =====
isupper()：判断字符串中的所有字母是否都是大写
islower()：判断字符串中的所有字母是否都是小写
isdigit()：检查字符串是否只包含数字
isalpha()：检查字符串是否只包含字母
isalnum()：检查字符串是否只包含字母和数字
isspace()：检查字符串是否只包含空白符

istitle()：检查字符串是否符合 ”标题化“
标题化规则：
1. 字符串中所有【单词】的首字母都是大写
2. 【单词】中其余的字母都是小写
3. 【单词】可以由非字母字符（空格、数字、标点符等）分隔

startswith(prefix)：检查字符串是否以 prefix 开头
endswith(suffix)：检查字符串是否以 suffix 结尾
"""
# print('HELLO'.isupper())
# print(('hello'.islower()))
# print("121ggg3".isdigit())
# print('hello'.isalpha())
# print('hello-123'.isalnum())-
# print("    ".isspace())
# print('Hello'.istitle())
# print('hello world'.startswith('wor'))
# print('hello world'.endswith('d'))


"""
===== 3. 查找与替换 =====
find(sub)：查找子字符串 sub 第一次出现的索引，如果不存在则返回 -1
rfind(sub)：查找子字符串 sub 最后一次出现的索引，如果不存在则返回 -1
index(sub)：查找子字符串 sub 第一次出现的索引，如果不存在则报错【ValueError】
rindex(sub)：查找子字符串 sub 最后一次出现的索引，如果不存在则报错【ValueError】
replace(old, new, count)：将字符串中的 old 子字符串替换为 new ，替换次数为 count【默认为全部替换】
count(sub)：统计子字符串 sub 出现的次数，可以指定范围 [start, end)
"""
# print("abc".find("b"))
# print('abcdef-abc-cdea-123'.rfind('a'))
# print('abc'.index('b'))
# print('abcdef-abc-cdea-123'.replace('a', 'A', 2))
# print('abcdef-abc-cdea-123'.count('a', 0, 7))


"""
===== 4. 分割与拼接
split(sep)：根据分隔符 sep 将字符串分割成子字符串，并返回子字符串组成的列表
splitlines()：根据行结束符（\n、\r、\r\n）将字符串分割成子字符串，并返回子字符串组成的列表
join(iterable)：将可迭代对象 iterable 中的元素用调用字符串连接成一个字符串

partition(sep)：根据分隔符 sep 将字符串分割成三部分，返回一个包含三个元素的元组
1. 元组的第一个元素: sep 之前的部分。
2. 元组的第二个元素: sep 本身。
3. 元组的第三个元素: sep 之后的部分（即使后面还存在 sep 分隔符）


"""
csv_line = "name,age,city"
# print(csv_line.split(","))
text = "line1\nline2\r\nline3"
# print(text.splitlines())
words = ["I", "love", "Python"]
# print(" ".join(words))
# print("user@example.com@xxx".partition("@"))
# print("ab".partition("b"))


"""
===== 5. 对齐与填充
center(width, [fillchar])：返回一个长度为 width 的新字符串，原字符串居中显示，
width 小于字符串长度则返回原字符串

ljust(width, [fillchar])：返回一个长度为 width 的新字符串，原字符串在左边，右边用填充字符补齐，
width 小于字符串长度则返回原字符串

rjust(width, [fillchar])：返回一个长度为 width 的新字符串，原字符串在右边，左边用填充字符补齐，
width 小于字符串长度则返回原字符串

zfill(width)：用零填充，特殊版本的右对齐，它专门用于在字符串的左侧填充数字 0，通常用于处理数字编号。
可以自动处理正负号。如果字符串以 + 或 - 开头，0 会被填充在符号的后面。
"""
# print("python".center(20, '❤'))
# print("python".ljust(20, '❤'))
# print("python".rjust(20, '❤'))
# print("python".zfill(20))
# print("+42".zfill(5))
# print("-42".zfill(5))


"""
字符串知识总结

1. 创建：单引号、双引号、三引号、str()
2. 特性：有序、不可变
3. 访问：索引、切片
4. 运算：+、*、in、not in
5. 长度：len()
6. 查找：find()、rfind()、index()、rindex()、count()
7. 修改(返回新字符串)：replace()、strip()、upper()、lower()、capitalize()、title()、swapcase()
8. 拆分与拼接：split()、splitlines()、join()
9. 判断：startswith()、endswith()、isupper()、islower()、isdigit()、isalpha()、isalnum()、istitle()
10. 对齐：center()、ljust()、rjust()、zfill()
11. 格式化：f-string【推荐】、format()、%
12. 编码：encode()、decode()
13. 特殊字符串：转义字符、原始字符串[ r"" ]
"""
