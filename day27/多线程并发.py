"""
基于 threading 实现多线程并发，I/O 阻塞
"""


import threading
import time


def task(name, index):
    """定义任务"""
    print(f"{name} 开始执行")
    
    '线程1阻塞时，其他线程可以继续执行'
    if index == 1:
        time.sleep(2)  # 模拟 I/O 等待
        
    print(f"{name} 执行结束")


threads = []

"""创建并启动线程"""
for i in range(3):
    t = threading.Thread(target=task, args=(f"任务{i}", i))
    threads.append(t)
    t.start()


"注：输出中各个任务的先后顺序可能会随机交错(打印随机)，因为线程调度完全由操作系统内核决定"
for t in threads:
    t.join()
