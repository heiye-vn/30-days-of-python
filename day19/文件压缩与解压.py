"""
文件压缩与解压的常用方法
"""

import shutil
import tarfile
import zipfile
from pathlib import Path

""" ZIP 压缩 """
# 创建 ZIP 压缩文件
# with zipfile.ZipFile("archive.zip", "w", zipfile.ZIP_DEFLATED) as zf:
#     zf.write("data/sample.txt", "sample.txt")
#     zf.write("data/sample.json", "sample.json")

# 解压 ZIP 文件
# with zipfile.ZipFile("archive.zip", "r") as zf:
#     zf.extractall("extracted/")  # 解压到目录
#     file_list = zf.namelist()  # 查看文件列表
#     content = zf.read("sample.txt")  # 读取文件内容
#     print(content)

# 查看 ZIP 信息
# with zipfile.ZipFile("archive.zip", "r") as zf:
#     for info in zf.infolist():
#         print(f"{info.filename}: {info.file_size} bytes")


""" TAR 压缩 """
# 创建 tar.gz 文件
# with tarfile.open("archive.tar.gz", "w:gz") as tf:
#     tf.add("data", arcname="data")

# 解压 tar.gz 文件
# with tarfile.open("archive.tar.gz", "r:gz") as tf:
#     tf.extractall("extracted_tar/")


""" shutil 快捷压缩 """
# 压缩整个目录
# shutil.make_archive("backup", "zip", "data")
# shutil.make_archive("backup", "gztar", "data")

# 解压
# shutil.unpack_archive("backup.zip", "output_dir")


# Path("backup.tar.gz").unlink()
# shutil.rmtree("output_dir")
