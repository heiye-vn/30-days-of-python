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


def convert_date_format(text):  # noqa
    """将 YYYY-MM-DD 格式的日期转换为 YYYY/MM/DD"""

    def replace_date(match):
        year = match.group(1)
        month = match.group(2)
        day = match.group(3)
        return f"{year}/{month}/{day}"

    return re.sub(r"(\d{4})-(\d{2})-(\d{2})", replace_date, text)


text = "项目开始于 2023-01-15，预计在 2024-06-30 完成。"
# print(convert_date_format(text))


"""
5. 密码强度检测
"""


def check_password_strength(password):
    """检查密码强度"""
    issues = []

    if len(password) < 8:
        issues.append("密码长度至少 8 位")
    if not re.search(r"[A-Z]", password):
        issues.append("需要包含至少一个大写字母")
    if not re.search(r"[a-z]", password):
        issues.append("需要包含至少一个小写字母")
    if not re.search(r"\d", password):
        issues.append("需要包含至少一个数字")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        issues.append("需要包含至少一个特殊字符")

    if not issues:
        return "密码强度：强"
    else:
        return "密码需要改进：\n" + "\n".join(f" - {issue}" for issue in issues)


# print(check_password_strength("Abc123!@#"))
# print(check_password_strength("abc12345"))


"""
6. 从文本中提取所有 IP 地址
"""
log_text = """
[INFO] Connection from 192.168.1.100 on port 8080
[WARN] Failed login from 10.0.0.55
[ERROR] Timeout connecting to 172.16.254.1:3306
[ERROR] Timeout connecting to 255.255.255.255:3307
"""

"""
匹配 IPV4 地址，表达式拆解分析
\b  (...\\.){3}  (...)  \b
│      │          │     │
│      │          │     └── 单词边界（右）
│      │          └── 第4段数字（最后一段，无点号）
│      └── 前3段「数字 + .」重复3次
└── 单词边界（左）

💡：\b 单词边界确保不会匹配到类似 1234.5.6.7 或 1.2.3.456 这种嵌在更长数字中的片段。
"""
ip_pattern = r"\b(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\b"
ips = re.findall(ip_pattern, log_text)
# print(ips)


"""
7. 空白规范化（RAG）
"""
raw = "这是   一段    从PDF提取的文本，\n\n\n包含多余的空白\t\t和换行符。   "
cleaned = re.sub(r"\s+", " ", raw).strip()
# print(cleaned)


"""
8. 章节标题提取（RAG）
按结构切分文档
"""
rag_text = """第一章 绪论
正文内容...

第二章 相关工作
正文内容...

Chapter 3: Methodology
正文内容..."""

pattern = r'^(第[一二三四五六七八九十百\d]+章\s+.+|Chapter\s+\d+[:：]\s*.+)$'
# print(re.findall(pattern, rag_text, re.MULTILINE))


"""
9. 中英混排句子切分（RAG）
用于 chunking 前的句子切分
"""
chunk_text = "这是第一句话。这是第二句！This is English. Another sentence!"
sentences = re.split(r"(?<=[。！？.!?])\s*", chunk_text)
sentences = [s for s in sentences if s]
# print(sentences)


"""
10. 清除页眉页脚噪音（RAG）
"""
word_text = "正文第一段。\n第 3 页 共 20 页\n正文第二段。"
clean = re.sub(r'第\s*\d+\s*页\s*共\s*\d+\s*页\n?', '', word_text)
print(clean)

"""
11. 提取邮箱/URL 等元数据（RAG）
"""
project_text = "联系: zsp@example.com, 项目: https://github.com/zsp/rag-demo"
print(re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', project_text))
print(re.findall(r'https?://[\w./\-]+', project_text))
