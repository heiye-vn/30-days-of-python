"""
文件路径与目录操作
"""

import shutil
import urllib.request
from pathlib import Path

"""
shutil（⭐⭐⭐⭐⭐）
shutil 模块提供了高级文件操作：复制、移动、压缩、删除非空目录等
它和 pathlib 是完全无缝融合、高度兼容的。所有的 shutil 函数都可以直接接受 Path 对象
"""

""" 复制文件 """
source_file = Path("data/sample.txt")
# shutil.copy("data/sample.txt", "data/sample_copy.txt")  # 复制内容+权限
# shutil.copy2(source_file, "data/sample_copy2.txt")  # 复制文件+元数据（时间戳等）


""" 复制目录 """
# 复制整个目录树 dirs_exist_ok=True 表示如果目标目录存在则覆盖
# shutil.copytree("data/subdir", "data/subdir_copy", dirs_exist_ok=True)


""" 移动文件/目录 """
# shutil.move("data/sample_copy.txt", "data/subdir/sample.txt")


""" 删除目录 """
# shutil.rmtree("data/subdir_copy")  # 删除整个目录树


"""
磁盘使用情况
total: 磁盘总容量
used: 已使用的容量
free: 剩余可用的容量 
"""
total, used, free = shutil.disk_usage("D:\\")
# print(f"Total: {total // (2**30)} GB")
# print(f"Used: {used // (2**30)} GB")
# print(f"Free: {free // (2**30)} GB")


""" 获取文件类型 """
# print(shutil.which("python"))  # 查找系统环境变量中可执行文件路径


"""
压缩、解压文件
压缩支持的格式：zip, tar, gztar, bztar, xztar
"""
# shutil.make_archive("data_compression", "zip", "data")
# shutil.make_archive("data_compression", "tar", "data")
# print(shutil.get_archive_formats())  # 获取支持的压缩格式
# print(shutil.get_unpack_formats())  # 获取支持的解压格式
# shutil.unpack_archive("data_compression.zip", "unpacked_data")

# Path("data_compression.zip").unlink(missing_ok=True)


""" 获取终端（控制台）窗口大小 """
size = shutil.get_terminal_size(fallback=(80, 24))
# print(f"当前终端宽度（列数）：{size.columns}")
# print(f"当前终端高度（行数）：{size.lines}")
# 打印一条刚好铺满屏幕的分割线
# print("-" * size.columns)


"""
流式复制文件对象
普通的 shutil.copy() 只能接收路径参数，而 copyfileobj 接收的是已经打开的文件对象（类文件对象，如网络请求返回的数据流、内存中的 StringIO 等）
"""
# 从网络下载图片，直接流式写入本地文件，避免一次性加载到内存中
img_url = "https://zsp-resource.oss-cn-chengdu.aliyuncs.com/%E5%A9%9A%E7%BA%B1%E7%85%A7/DSC09665.jpg"
# with urllib.request.urlopen(img_url) as response, open("my_girl.jpg", "wb") as out_file:
#     shutil.copyfileobj(response, out_file)
