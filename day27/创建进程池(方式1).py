
"""
multiprocessing.Pool 创建进程池
"""

from multiprocessing import Pool
import os
import time


def task(num):
    print(f"进程 {os.getpid()} 正在处理任务：{num}")
    time.sleep(1)
    return num * num


if __name__ == "__main__":
    # 创建进程池，最多同时运行 3 个进程
    with Pool(processes=3) as pool:

        # 批量执行任务，并获取结果
        results = pool.map(task, range(1, 11))

        print("计算结果：", results)
