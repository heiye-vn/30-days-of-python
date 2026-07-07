"""
综合案例：插件式任务系统
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class TaskResult:
    name: str
    success: bool
    message: str = ""
    data: dict = field(default_factory=dict)


class Timer:
    def __init__(self, label):
        self.label = label

    def __enter__(self):
        self.start = time.perf_counter()

    def __exit__(self, exc_type, exc_val, traceback):
        self.end = time.perf_counter()
        self.elapsed = self.end - self.start
        print(f"{self.label} 耗时：{self.elapsed:.8f} 秒:")
        return False


class Task(ABC):
    registry = {}

    # 自动注册任务类
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not getattr(cls, "abstract", False):
            Task.registry[cls.__name__] = cls

    @abstractmethod
    def run(self):
        pass

    # 让对象可以像函数一样调用
    def __call__(self):
        with Timer(self.__class__.__name__):  # noqa
            return self.run()


class CountTask(Task):
    def __init__(self, limit):
        self.limit = limit

    def run(self):
        total = sum(range(self.limit + 1))
        return TaskResult(
            name="count", success=True, message="计算完成", data={"total": total}
        )


class HelloTask(Task):
    def __init__(self, name):
        self.name = name

    def run(self):
        return TaskResult(name="hello", success=True, message=f"你好，{self.name}")


tasks = [CountTask(100), HelloTask("Alice")]

for task in tasks:
    result = task()
    print(result)

print(Task.registry)
