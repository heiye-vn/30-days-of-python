"""
正则匹配示例演示
"""

import re

"""
1. 验证邮箱地址
"""


def is_valid_email(email):
    """简单验证邮箱格式是否合法"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


# 测试
# print(is_valid_email("user@example.com"))
# print(is_valid_email("test.name@company.cn"))
# print(is_valid_email("invalid@.com"))
# print(is_valid_email("no_at_sign.com"))


"""
2. 提取网页中的所有链接
"""
html = """
<a href="https://www.python.org">Python 官网</a>
<a href="https://docs.python.org">Python 文档</a>
<img src="https://example.com/logo.png">
<a href="http://docs.node.org">Node.js 文档</a>
"""
# 提取所有 href/src 属性中的 URL
links = re.findall(r'(href|src)="(https?://[^"]+)', html)
# for link in links:
#     print(link[1])


"""
3. 验证中国大陆手机号 
"""


def is_valid_phone(phone):
    """验证中国大陆手机号（11 位，1 开头，第二位为 3-9）"""
    pattern = r"^1[3-9]\d{9}$"
    return bool(re.match(pattern, phone))


# print(is_valid_phone("13812345678"))
# print(is_valid_phone("12345678901"))
# print(is_valid_phone("1381234567"))


"""
4. 解析日期格式并转换
"""


def convert_date_format(text):
    """将 YYYY-MM-DD 格式的日期转换为 YYYY/MM/DD"""

    def replace_date(match):
        year = match.group(1)
        month = match.group(2)
        day = match.group(3)
        return f"{year}/{month}/{day}"

    return re.sub(r"(\d{4})-(\d{2})-(\d{2})", replace_date, text)


text = "项目开始于 2023-01-15，预计在 2024-06-30 完成。"
print(convert_date_format(text))
