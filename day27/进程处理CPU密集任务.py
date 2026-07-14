"""
如果任务是 CPU 密集型，多线程通常不一定能明显加速
"""

from concurrent.futures.process import ProcessPoolExecutor

"""
使用进程池（ProcessPoolExecutor）
"""


# 计算数字范围内的素数（质数）的个数
def count_primes(limit: int) -> int:
    count = 0

    for number in range(2, limit):
        is_prime = True

        for factor in range(2, int(number**0.5) + 1):
            if number % factor == 0:
                is_prime = False
                break

        if is_prime:
            count += 1

    return count


def main() -> None:
    limits = [50_000, 60_000, 70_000, 80_000]

    with ProcessPoolExecutor() as executor:
        results = executor.map(count_primes, limits)

        for limit, result in zip(limits, results):
            print(limit, result)


if __name__ == "__main__":
    main()


"""
以上示例为什么选择多进程（Process）而非多线程（Thread）？

在 Python 中，受 GIL（Global Interpreter Lock，全局解释器锁） 的限制，同一时刻只有一个线程能在 CPU 上运行 Python 字节码
"""
