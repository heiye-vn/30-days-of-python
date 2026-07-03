"""
正则练习
"""

import re

"""
1. 写一个函数，验证用户输入的身份证号是否合法（18 位，最后一位可能是 X）
"""


def is_valid_id(id_card):
    pattern = r"^\d{17}[\dX]$"
    return bool(re.match(pattern, id_card))


# print(is_valid_id("513721199808267538"))
# print(validator.is_valid("513721199808267538"))
# print(validator.get_info("131002198807175389"))


"""
2. 从一段英文文本中找出所有以大写字母开头的单词
"""
text = "Hello World. This is a test. This is only a test."
matches = re.findall(r"[A-Z]\w*", text, re.MULTILINE)
# print(matches)


"""
3. 把一个字符串中的连续重复字符压缩成一个（如 aaabbbccc → abc）
"""
repeat_text = "aaabbbccc"
# print("".join(re.findall(r"(\w)\1*", repeat_text)))


"""
4. 写一个简单的计算器，能从字符串中提取所有数字（包括小数和负数）
"""
calc_text = "收入100.5元，支出-20元，剩余80.5元。气温是-5.5度，整数部分是3。"
numbers = re.findall(r"-?\d+(?:\.\d+)?", calc_text)
# parsed_numbers = [float(n) for n in numbers]
print(numbers)
# print("提取数字:", parsed_numbers)


"""
5. 验证一个字符串是否是合法的 URL（考虑 http/https、域名、路径、查询参数等）
"""
url_pattern = (
    r"^https?://([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%]*)?$"
)
# print(re.match(url_pattern, "https://www.example.com/path/to/resource?query=param"))
