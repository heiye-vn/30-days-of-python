"""
文件路径与目录操作
"""

import os

"""
os / os.path
os.path 模块是传统的路径操作方式

os.path 的本质：面向字符串，路径相关操作需要手动拼接
"""

""" 路径拼接 """
file_path = os.path.join("data", "sample.txt")
# print(path)

""" 路径拆分 """
dirname, filename = os.path.split("data/sample.txt")
# print(dirname, filename)
name, ext = os.path.splitext("sample.txt")
# print(name, ext)

""" 路径信息 """
# print(os.path.basename(file_path))  # sample.txt
# print(os.path.dirname(file_path))  # data
# print(os.path.abspath(file_path))  # 绝对路径
# print(os.path.exists("data/xxx.mp4"))  # 判断文件路径是否存在
# print(os.path.isfile(file_path))
# print(os.path.isfile("data/xxx.mp4"))  # 判断是否是文件并且存在
# print(os.path.isdir("data/subdir"))  # 判断是否是目录并且存在
# print(os.path.getsize(file_path))  # 文件字节数


""" 创建目录 """
# os.mkdir("new_folder")
# makedirs()，递归创建多层目录
# os.makedirs("new_folder/a/b", exist_ok=True)


"""
删除目录
💡：pathlib 和 os 均无法删除非空目录，需使用 shutil 模块
"""
# os.rmdir("data/subdir")
# os.rmdir("new_folder/a/b")
# os.removedirs("new_folder/a")  # 删除多级目录


""" 文件遍历 """
target_dir = "data"
for item in os.listdir(target_dir):
    # 1. 拼接成完整路径，如 "data/subdir"
    full_path = os.path.join(target_dir, item)

    # 2. 对完整路径进行类型判断
    is_directory = os.path.isdir(full_path)

    # 3. 打印结果
    print(f"{'[DIR]' if is_directory else '[FILE]'} {item}")
