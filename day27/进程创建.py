
"""
基于 multiprocessing 创建多进程
"""

import multiprocessing
import os
import time


def task(name):
    print(f"任务 {name} 开始执行，进程 ID：{os.getpid()}")
    time.sleep(2)
    print(f"任务 {name} 执行结束")


if __name__ == "__main__":
    # 创建进程对象
    p1 = multiprocessing.Process(target=task, args=("A",))
    p2 = multiprocessing.Process(target=task, args=("B",))

    # 启动子进程
    p1.start()
    p2.start()

    # 等待进程执行结束
    p1.join()
    p2.join()

    print("所有进程执行完毕")
