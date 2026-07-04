"""
文件路径与目录操作
"""

from datetime import datetime
from pathlib import Path

"""
pathlib（⭐⭐⭐⭐⭐）
pathlib 模块提供了一种面向对象的方式来处理文件系统路径，使得文件路径的处理更加直观和方便。
💡：在底层的操作系统级别，所有的文件系统操作（如判断是否存在、读取、写入等）最终都必须定位到绝对路径。

pathlib 的本质：面向对象，每一个 Path 对象都完整保留了它的上下文信息
"""

""" 1 创建路径对象 """
p = Path("data/sample.txt")
p_abs = Path("data/sample.txt").resolve()  # 绝对路径
# print(p)
# print(p_abs)

""" 2 路径拼接（使用 【 / 】运算符） """
base = Path("data")
file_path = base / "subdir" / "file.txt"
# print(file_path)

""" 3 获取路径对象相关信息 """
# print(p.name)  # sample.txt（文件名，包括扩展名）
# print(p.stem)  # sample（文件名，不包括扩展名）
# print(p.suffix)  # .txt（文件扩展名）
# print(p.parent)  # data（文件所在目录，父目录）
# print(p.parts)  # ('data', 'sample.txt')，路径的各个部分组成的元组
# print(p_abs.parts)
# print(p.exists())  # 文件是否存在，True
# p_ = Path("data/subdir/test.txt")
# print(p_.exists())  # False
# print(p.is_file())  # True，判断路径对象是否是一个文件，并且存在（以绝对路径判断）
not_file = Path("day19/data")
# print(not_file.is_file())
# print(p.is_dir())  # 判断路径对象是否是一个目录，并且存在（以绝对路径判断）
# print(not_file.is_dir())

""" 4 获取文件大小和修改时间 """
if p.is_file():
    file_info = p.stat()
    # 文件大小（单位：字节）
    # print(f"文件大小：{file_info.st_size} 字节")
    # 最后修改时间，返回时间戳
    modify_time = datetime.fromtimestamp(file_info.st_mtime)
    # print(f"最后修改时间：{modify_time}")
    create_time = datetime.fromtimestamp(file_info.st_ctime)
    # print(f"创建时间：{create_time}")

"""
5. 快捷读写文件内容
pathlib 提供了非常便捷的直接读写方法，不需要手动使用 with...open() 语句
但是 read_text()/read_bytes() 不适合读取大文件
可以使用 Path.open() 方法来读取大文件，和内置的 open() 方法一样
"""
# 一次性读取文件所有文本内容
content = p.read_text(encoding="utf-8")
# print(content)
# with p.open(mode="r", encoding="utf-8") as f:
#     for line in f:
#         print(f"逐行读取：{line.strip()}")


# 一次性写入/覆盖文本内容
# new_p = Path("data/new_sample.txt")
# new_p.write_text("Hello Python123\nThis is a new file.", encoding="utf-8")


""" 6. 创建、删除、重命名操作 """
# new_file = Path("data/rename_sample.txt")
# 创建文件，exist_ok=True，如果文件存在则不报错
# new_file.touch(exist_ok=True)
# 重命名/移动文件
# target_file = Path("data/rename_sample.txt")
# new_file.rename(target_file)
# move_file = Path("moved_sample.txt")
# new_file.rename(move_file)
# 删除文件，missing_ok=True，文件不存在也不会报错
# del_file = Path("moved_sample.txt")
# del_file.unlink(missing_ok=True)
# 删除空目录（非空会报错）
# Path("data/empty_dir").rmdir()

""" 7. 创建目录 """
# parents=True，递归创建多级目录，exist_ok=True，如果目录存在则不报错
Path("data/subdir").mkdir(parents=True, exist_ok=True)


""" 8. 遍历目录 """
# 只遍历当前层
# for i in Path("data").iterdir():
#     print(i)

# glob(): 匹配所有符合模式的文件路径（只在当前目录）
# for i in Path("data").glob("*.txt"):
#     print(f"txt 文件：{i.resolve()}")

# rglob(): 递归所有子目录匹配所有符合模式的文件路径
# for i in Path("data").rglob("*"):
#     # 确保是文件，且后缀在指定范围内
#     if i.is_file() and i.suffix in (".txt", ".csv"):
#         print(f"递归遍历文件：{i.resolve()}")

data_dir = Path("data")
for item in data_dir.iterdir():
    print(f"{'[DIR]' if item.is_dir() else '[FILE]'} {item.name}")
