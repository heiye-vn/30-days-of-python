import re

"""
1. 普通字符
字母、数字、汉字等普通字符在正则中直接匹配自身
"""
text = "I have a dog and a cat."
result = re.search(r"cat", text)
# print(f"result: {result}") # result: <re.Match object; span=(19, 22), match='cat'>
# print(result.group())  # noqa

"""
2.1 元字符【 . 】
匹配除换行符 [ \n ] 外的任意单个字符
📌应用场景：匹配任意字符（如密码校验中“至少含一个非空字符”）
"""
text1 = "a b\nc"
# print(re.findall(r".", text1))  # ['a', ' ', 'b', 'c']
# 注：默认 . 不匹配换行符 \n，若要匹配换行符 \n，则需使用 [ re.DOTALL ] 或 [ re.S ]
# print(re.findall(r".", text1, re.DOTALL))  # ['a', ' ', 'b', '\n', 'c']


"""
2.2 元字符【 ^ 】
匹配字符串的开始位置，或行的开始位置（需使用 [ re.MULTILINE ] 或 [ re.M ] ）
💡 ^ 在方括号（[]）中表示“否定”的意思，即匹配不在方括号中的字符
"""
text2 = "First line\nSecond line\nSuccess info"
# print(re.findall(r"^F", text2))  # ['F']
# print(re.findall(r"^S", text2, re.MULTILINE))  # ['S', 'S']
# print(re.findall(r"[^A-Za-z ]", "这是一段测试, this is tested text, 123"))


"""
2.3 元字符【 $ 】
匹配字符串的结尾位置，或行的结尾位置（需使用 [ re.MULTILINE ] 或 [ re.M ] ）
📌 实用技巧：验证字符串是否以某内容结尾
"""
text3 = "abc\nxyz"
# print(re.findall(r"c$", text3))  # []
# print(re.findall(r"c$", text3, re.M))  # ['c']
# print(re.findall(r"yz$", text3))  # ['yz']


"""
2.4 元字符【 * 】
匹配前面一个字符 0 次或多次（贪婪匹配）, 使用 () 可以包裹多个字符匹配
💡 警告： .* 是“万能通配”，但可能过度匹配（贪婪性），字符串末尾也会匹配
"""
text4 = "aaabbb"
# print(re.findall(r"a*", text4))  # ['aaa', '', '', '', '']，字符串末尾同样也可以匹配 0 个 a
# print([m for m in re.findall(r"a*", text4) if m])  # ['aaa']
# a.*：表示以 a 开头，后面跟着任意数量的任意字符
# print(re.findall(r"a.*", "Apple and banana are fruits"))
# 匹配 "ab*"：a 后跟 0 或多个 b
# print(re.findall(r"ab*", "a ab abb abbb"))  # noqa ['a', 'ab', 'abb', 'abbb']
# print(re.findall(r"(ab)*", "a ab abb abbb"))  # noqa


"""
2.5 元字符【 + 】
匹配前面一个字符 1 次或多次
"""
text5 = "aaabbb"
# print(re.findall(r"a+", text5))  # ['aaa']
# print(re.findall(r"ab+", "a ab abb abbb"))
# print(re.findall(r"(ab)+", "a ab abb, abbb"))


"""
2.6 元字符【 ? 】
匹配前面一个字符 0 次或 1 次
💡 常用于：拼写变体（behaviour/behavior）、可选后缀（https?:// 匹配 http 或 https）
"""
text6 = "color colour"
# print(re.findall(r"colou?r", text6))  # # ['color', 'colour']（u 可有可无）
# cm? 不是 cm 可选，而是 m 可选，c必须有
# print(re.findall(r"\d+\.?\d*cm?", "10cm 12.5 3.14cm"))  # ['10cm', '3.14cm']
# 非捕获分组
# print(re.findall(r"\d+\.?\d*(?:cm)?", "10cm 12.5 3.14cm"))  # ['10cm', '12.5', '3.14cm']


"""
2.7 元字符【 {m} 】
连续切出 m 个
匹配前面的元素连续且恰好出现 m 次
📌 注意：必须连续出现 m 次，不能间隔
"""
text7 = "aaaa bbb cc"
# print(re.findall(r"a{3}", text7))  # ['aaa']
# print(re.findall(r"b{2}", text7))  # ['bb']


"""
2.8 元字符【 {m,n} 】
连续切出 m 到 n 个（贪婪优先）
匹配前面的元素连续出现最少 m 次，最多 n 次
💡{m,} 表示无上限

{0,1} <=> ?
{1,} <=> +
{0,} <=> *
"""
text8 = "a aa aaa aaaa"
# print(re.findall(r"a{2,3}", text8))  # ['aa', 'aaa', 'aaa']
# print(re.findall(r"a{3,}", text8))  # ['aaa', 'aaaa']
# print(re.findall(r"a{0,}", text4)) # ['aaa', '', '', '', '']


"""
2.9 元字符【 [] 】，也叫字符集合
匹配方括号内的任意一个字符
💡注：特殊字符在 [] 内会失去原有含义（除 ^, -, \），变成普通的字符匹配
"""
text9 = "abc12.3XYZ."
# 匹配元音字母
# print(re.findall(r"[aeiou]", text9))  # ['a']
# print(re.findall(r"[aeiou]", "Hello World"))
# print(re.findall(r"[a-z]", text9))  # ['a', 'b', 'c']
# 匹配字母（大小写）
# print(re.findall(r"[a-zA-Z]", text9))  # ['a', 'b', 'c', 'X', 'Y', 'Z']
# 匹配数字
# print(re.findall(r"[0-9]", text9))
# print(re.findall(r"[0-9]", "I have 3 cats and 2 dogs"))
# print(re.findall(r"[.]", text9))  # [] 方括号里的 . 不是表示任意字符，而是表示实际的 . 字符
# 取反：^ 放在括号内第一个位置，表示”不在范围内“
# print(re.findall(r"[^b]", text9))
# print(re.findall(r"[^0-9]", "a1b2c3"))
# print(re.findall(r"[a^]", text9))  # 这里的 [a^] 表示匹配 a 或 ^


"""
2.10 元字符【 | 】
匹配左右任意一个表达式
📌 实用场景
- 多关键词搜索：r"error|warning|fatal"
- 多格式日期：yyyy-mm-dd | mm/dd/yyyy
"""
text10 = "cat dog bird"
# print(re.findall(r"cat|dog|bird", text10))
# print(re.findall(r"\d+|hello", "123 hello 456"))
# print(re.findall(r"he|llo", "hello"))
# print(re.findall(r"hel|lo", "hello"))


"""
2.11 元字符【 () 】，也叫分组捕获（捕获组）
括号用于分组，也可以用于捕获
"""
text11 = "Email: user@example.com, Phone: 123-456-7890"
pattern = r"Email: (\S+@\S+\.\S+)"
match = re.search(pattern, text11)
# print(match.group(1))
pattern2 = r"(?:Email|Phone): (\S+)"
# print(re.findall(pattern2, text11))

# 提取日期中的年、月、日
date = "Today is 2023-10-02"
match = re.search(r"(\d{4})-(\d{2})-(\d{2})", date)
# if match:
#     print(match.group(0))  # 返回整个匹配
#     print(match.group(1))  # 返回第一个捕获组
#     print(match.group(2))  # 返回第二个捕获组
#     print(match.group(3))  # 返回第三个捕获组
#     print(match.group())  # 返回整个匹配
#     print(match.groups())  # 返回所有捕获组组成的元组

# 命名分组：用 (?P<name>...) 给组起一个名称
match_ = re.search(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})", "2023-10-02")
# print(match_.group("year"))  # 2023
# print(match_.group("month"))  # 10
# print(match_.group("day"))  # 02


"""
2.12 元字符【 \\ 】
转义，让元字符失去特殊含义，匹配实际的字符，或引入特殊序列（预定义字符类）
"""
text12 = "price: $10.50"
# 转义元字符：匹配字面 '.' 或 '$'
# print(re.findall(r"\$\d+", text12))
# print(re.findall(r"\.", "a.b.c"))

# 引入特殊序列：
# print(re.findall(r"\d", "abc123"))
# print(re.findall(r"\w", "a_b 123"))
# print(re.findall(r"\s", "a b\nc"))

# 转义反斜杠本身：r"\\\\" 或 "\\"
# print(re.findall(r"\\", "path\\file"))


"""
常见的预定义字符类（用 \\ 转义，避免控制台报错）
\\d <=> [0-9]，匹配数字
\\D <=> [^0-9]，匹配非数字
\\w <=> [a-zA-Z0-9_]，匹配字母、数字、下划线
\\W <=> [^a-zA-Z0-9_]，匹配非字母、数字、下划线
\\s <=> [ \t\n\r\f\v]，匹配空白字符
\\S <=> [^ \t\n\r\f\v]，匹配非空白字符
\\b <==> \b 匹配单词边界

💡在正则表达式的底层，所有的 字母、数字和下划线(_)都被视作单词字符
"""
text13 = "Python 3.12 was released on 2023-10-02"
# 提取所有数字
# print(re.findall(r"\d+", text13))

# 提取所有单词
# print(re.findall(r"\w+", text13))  # 所有单词
# print(re.findall(r"\b[a-zA-Z]+\b", text13))  # 纯英文单词

# 提取空白字符分隔
print(re.split(r"\s+", text13))
