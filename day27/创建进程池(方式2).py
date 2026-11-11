
"""
ProcessPoolExecutor 创建进程池（推荐）
"""

from concurrent.futures import ProcessPoolExecutor
import os


def calculate(num):
    print(f"进程 {os.getpid()} 正在计算：{num}")
    return num * num


if __name__ == "__main__":

    # 创建进程池，最多 3 个工作进程
    with ProcessPoolExecutor(max_workers=3) as executor:

        # 提交多个任务
        futures = [
            executor.submit(calculate, i)
            for i in range(1, 11)
        ]

        # 获取任务结果
        results = [future.result() for future in futures]

        print("计算结果：", results)
