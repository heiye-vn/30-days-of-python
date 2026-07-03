"""
在 Python 中，文件处理是一项非常基础且常用的技能。不管是读取配置文件、解析 CSV 数据，还是写入日志，都离不开文件操作
"""

from typing import Final

TXT_ENCODING: Final[str] = "utf-8"

"""
1. 打卡与关闭文件
在 Python 中，文件的打开和关闭是通过内置函数 `open()` 和 `close()` 来实现的。

但是手动执行 close()，在某些情况下可能不会触发或者忘记执行

⭐️⭐️⭐️⭐️⭐️：推荐使用 【 with 】 语句结合 open() 来打开文件。
在 Python 中，with 语句是一个用于自动管理资源的控制流结构，它与上下文管理器（Context Manager）配合使用
核心作用：确保无论代码是正常执行完毕，还是在执行过程中发生异常，申请的资源（如文件、数据库连接、线程锁等）都会被自动、安全地释放。防止内存泄漏和文件损坏

💡：encoding 编码模式默认是 "utf-8"，但是可能有些系统的默认编码不是这个，所以推荐显示指定编码模式。实际项目中更稳妥的方式是用 chardet 
或 charset-normalizer 检测编码，再用检测结果打开文件。
"""
# with open("data/sample.txt", "r", encoding=TXT_ENCODING) as file:
#     content = file.read()
#     print(content)

"""
2. 读取文件
- read()，可以指定读取的字节数，不指定则读取全部内容
- readline()
- readlines()

💡：处理大文件时优先使用逐行迭代（for line in file），而不是 read() 或 readlines()，避免一次性加载占用大量内存
"""
# 读取全部内容
# with open("data/sample.txt", "r", encoding=TXT_ENCODING) as f:
#     content = f.read()
#     print(content)

# 按行读取（返回所有行的列表）
# with open("data/sample.txt", 'r', encoding=TXT_ENCODING) as f:
#     lines = f.readlines()
#     print(lines)
#     for line in lines:
#         print(line.strip())

# 逐行读取（内存友好，适合大文件）
# with open("data/sample.txt", "r", encoding=TXT_ENCODING) as f:
#     for line in f:
#         print(line.strip())

# 读取指定字节数
# with open("data/sample.txt", "r", encoding=TXT_ENCODING) as f:
#     chunk = f.read(50)  # 读取前 50 个字符
#     print(chunk)
#     print(len(chunk))

# 读取一行
# with open("data/sample.txt", "r", encoding=TXT_ENCODING) as f:
#     line = f.readline()
#     print(line)


"""
3. 写入文件
- write(): 单行写入
- writelines(lines): 多行写入，写入列表
"""
# 覆盖写入（"w" 模式会清空原内容）
# with open("data/output.txt", "w", encoding=TXT_ENCODING) as f:
#     f.write("Hello, World!\n")
#     f.write("Python file handing.\n")

# 写入多行
# lines = ["第一行\n", "第二行\n", "第三行\n"]
# with open("data/output.txt", "w", encoding=TXT_ENCODING) as f:
#     f.writelines(lines)

# 追加写入（"a" 模式不会清空原内容）
# with open("data/output.txt", "a", encoding=TXT_ENCODING) as f:
#     f.write("追加新的内容\n")

"""
4. 文件指针
- tell(): 获取当前文件指针位置
- seek(offset, whence): 移动文件指针位置
"""
# with open("data/sample.txt", "r", encoding=TXT_ENCODING) as f:
#     print(f.tell())  # 输出当前文件指针位置
#     f.seek(10)  # 移动文件指针到第 10 个字节
#     print(f.tell())  # 输出当前文件指针位置
#     f.seek(5)
#     print(f.tell())


"""
5. 常见文件模式
- "r": （默认）只读，文件不存在则报错
- "w": 只写，覆盖写入，文件存在则清空重写，不存在则创建
- "a": 追加写，文件不存在则创建，存在则末尾追加
- "x": 独占创建，文件已存在则报 FileExistsError，不存在则创建
- "+": 读写模式
- "r+": 读写
- "w+": 读写，覆盖写入
- "a+": 读写，追加写入
- "b": 二进制模式，需组合使用，如 'rb'、'wb'
- "t": 文本模式，默认模式，通常省略不写
"""
# 二进制读取
# with open("data/image.png", "rb") as f:
#     binary_data = f.read()

# print(binary_data)

# 二进制写入
# with open("data/image_copy.png", 'wb') as f:
#     f.write(binary_data)

# 更推荐写法：分块读取写入，不会一次性占用大量内存
with open("data/image.png", "rb") as src, open("data/image_copy.png", "wb") as dst:
    while chunk := src.read(8192):  # 8192 字节（8kb），全部读完会返回空字节串，循环结束
        dst.write(chunk)
