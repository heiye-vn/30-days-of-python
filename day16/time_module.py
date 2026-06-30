"""
time 模块
模块偏向底层，直接调用 C 语言级别的系统时间 API。
它的效率极高，主要处理时间戳、系统延迟及 CPU 性能度量
"""

import time

# 获取当前时间戳
cur_timestamp = time.time()  # Unix 时间戳 (float)
# print(f"当前时间戳为：{cur_timestamp}")

# 时间戳转本地结构化时间
local_struct = time.localtime(cur_timestamp)
# print(f"本地年份：{local_struct.tm_year}，星期几：{local_struct.tm_wday}")  # 星期一（0） ~ 星期日（6）
utc_struct = time.gmtime(cur_timestamp)
# print(f"UTC 年份：{utc_struct.tm_year}，星期几：{utc_struct.tm_wday}")

# 结构化时间转时间戳
t_timestamp = time.mktime(local_struct)
# print(f"时间戳：{t_timestamp}")

# 结构化时间转格式化字符串
time_str = time.strftime("%Y-%m-%d %H:%M:%S", local_struct)
# print(f"格式化输出：{time_str}")
# print(type(time_str))

# 字符串解析为结构化时间
parsed_struct = time.strptime("2026-06-30 18:30:00", "%Y-%m-%d %H:%M:%S")
# print(f"解析后的年份：{parsed_struct.tm_year}")

# 让当前线程休眠 1.5 秒
# time.sleep(1.5)
# print("休眠 1.5 秒后输出此句")

# 高精度计时
start = time.perf_counter()  # 性能计数器（纳秒级）
result = [x ** 2 for x in range(1000)]
elapsed = time.perf_counter() - start
# print(f"耗时：{elapsed:.6f} 秒")
