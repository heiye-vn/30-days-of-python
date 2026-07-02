"""
Python 的 re 模块提供了几种不同的方法来执行正则匹配，它们的侧重点各不相同
"""

import re

"""
1. re.match(pattern, string) —— 从开头匹配
只从字符串的【开头】开始匹配，返回 Match 对象。如果开头不符合，直接返回 None。
"""
# print(re.match(r"\d+", "123 abc").group())  # noqa 123
# print(re.match(r"\d+", "abc 123"))  # noqa None


"""
2. re.search(pattern, string) —— 搜索第一个匹配
在整个字符串中查找第一个匹配的位置，找到就返回一个 Match 对象，找不到返回 None。
💡注：re.search 比 re.match 更常用，因为 search 会在整个字符串中搜索，而 match 只看开头
"""
result2 = re.search(r"\d+", "abc 123 def 456")
print(result2.group())  # noqa 123
print(result2.start())  # noqa 4
print(result2.end())  # noqa 7

"""
3. re.findall(pattern, string) —— 找到所有匹配
返回一个列表，包含所有匹配的结果
如果正则中有分组， findall 会返回每个匹配中各组的元组（捕获组）
"""
text3 = "我的电话是 13812345678，朋友的是 13987654321"
phones = re.findall(r"1[3-9]\d{9}", text3)
# print(phones)

text_3 = "john@example.com, jane@test.org"
sites = re.findall(r"(\w+)@(\w+\.\w+)", text_3)
# print(sites)


"""
4. re.finditer(pattern, string) —— 迭代所有匹配
和 findall 类似，单返回的是 Match 对象的迭代器，适合处理大量匹配或需要获取位置信息的场景。
处理超大文本时，它不会一次性把所有结果加载到内存里，而是用一个吐一个，非常省内存
"""
text4 = "Python was created in 1991. Python 3 came out in 2008."
# for match in re.finditer(r"Python", text4):
#     print(f"找到 '{match.group()}'，位置：{match.span()}")


"""
5. reb.sub(pattern, repl, string) —— 替换
把所有匹配的部分替换为指定内容，返回一个新字符串。
"""
text5 = "我的电话是 13812345678，请记住。"
# 替换为固定字符串
result5 = re.sub(r"1[3-9]\d{9}", "***", text5)
# print(result5)


# 用函数动态替换：把数字部分遮盖
def mask_phone(match):
    phone = match.group()
    return phone[:3] + "****" + phone[-4:]


result5_ = re.sub(r"1[3-9]\d{9}", mask_phone, text5)
# print(result5_)

text_5 = "用户 A 的密码是 123456，用户 B 的密码是 abcd123"
# print(re.sub(r"是 \w+", "是 *****", text_5))


"""
6. re.split(pattern, string) —— 分割
按匹配的模式来分割字符串，返回 list 列表。
"""
# text6 = "apple, banana; orange|grape"
text6 = "apple,banana;orange grape"
# 按逗号、分好或竖线分割
# result6 = re.split(r"[,;|]\s*", text6)
result6 = re.split(r"[,;\s]+", text6)
# print(result6)  # ['apple', 'banana', 'orange', 'grape']
# 限制分割次数
result6_ = re.split(r"[,;|]\s*", text6, maxsplit=2)
# print(result6_)  # ['apple', 'banana', 'orange|grape']


"""
7. re.compile(pattern) —— 预编译
如果同一个正则要用很多次（比如批量清洗几百个 PDF 页面），先编译能避免重复解析正则语法，也让代码更清晰
返回一个 Pattern 对象，包含编译后的正则表达式
编译后可直接调用方法
"""
phone_pattern = re.compile(r"1[3-9]\d{9}")

text1 = "联系我：13800001111"
text2 = "号码 13900002222 有效"

# print(phone_pattern.findall(text1))  # ['13800001111']
# print(phone_pattern.search(text2).group())  # noqa 13900002222
# print(phone_pattern.sub("xxx", text1))

# VERBOSE 模式允许写注释和空白,复杂正则的可读性神器
date_pattern = re.compile(
    r"""
    (\d{4})   # 年
    -
    (\d{2})   # 月
    -
    (\d{2})   # 日
""",
    re.VERBOSE,
)
# print(date_pattern.match("2026-07-02").groups())  # noqa ('2026', '07', '02')
