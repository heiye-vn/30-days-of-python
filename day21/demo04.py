"""
任务调度系统
涉及：SOLID 原则、策略模式、观察者模式、建造者模式、组合优于继承
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Protocol


# ---------- 枚举与数据类 ----------
# 任务优先级枚举
class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


# 任务生命周期状态机
class TaskStatus(Enum):
    PENDING = "待执行"
    RUNNING = "执行中"
    SUCCESS = "成功"
    FAILED = "失败"
    CANCELLED = "已取消"


@dataclass
class TaskResult:
    """任务执行结果值对象，用 dataclass 自动生成 __init__ 等方法"""
    success: bool
    message: str
    duration_seconds: float = 0.0
    # field(default_factory=dict) 确保每个实例拥有独立的 dict，避免共享可变默认值
    data: dict = field(default_factory=dict)


# ---------- 事件系统（观察者模式）----------
class EventListener(Protocol):
    # “鸭子类型” 接口
    def on_event(self, event_type: str, task_id: str, detail: dict): ...


class EventBus:
    """事件总线：解耦事件的发布者与订阅者，实现观察者模式的核心中介"""

    def __init__(self):
        # 按事件类型分组存储监听器：{"task.started": [listener1, listener2], ...}
        self._listeners: dict[str, list[EventListener]] = {}

    def subscribe(self, event_type: str, listener: EventListener):
        # setdefault：键不存在时创建空列表，避免 KeyError
        self._listeners.setdefault(event_type, []).append(listener)

    def unsubscribe(self, event_type: str, listener: EventListener):
        if event_type in self._listeners:
            self._listeners[event_type].remove(listener)

    def publish(self, event_type: str, task_id: str, detail: dict):
        """发布事件，通知该类型下的所有监听器"""
        for listener in self._listeners.get(event_type, []):
            listener.on_event(event_type, task_id, detail or {})


class ConsoleLogger:
    """日志监听器：将事件以带时间戳的格式输出到控制台"""

    def on_event(self, event_type: str, task_id: str, detail: dict):  # noqa
        time = datetime.now().strftime("%H:%M:%S")
        print(f"  [{time}] [{event_type}] 任务 {task_id}: {detail}")


class MetricsCollector:
    """指标收集器：按事件类型累计计数，用于生成统计报表"""

    def __init__(self):
        self.counts: dict[str, int] = {}

    def on_event(self, event_type: str, task_id: str, detail: dict):  # noqa
        # dict.get 提供默认值 0，避免首次访问时 KeyError
        self.counts[event_type] = self.counts.get(event_type, 0) + 1


# ---------- 任务执行器（策略模式）----------
class TaskExecutor(ABC):
    """任务执行策略的抽象基类，新增执行方式只需继承此类（开闭原则 OCP）"""

    @abstractmethod
    def execute(self, task_id: str, params: dict) -> TaskResult:
        """子类必须实现此方法，定义具体的执行逻辑"""
        ...


class ShellExecutor(TaskExecutor):
    """Shell 命令执行策略"""

    def execute(self, task_id: str, params: dict) -> TaskResult:
        command = params.get("command", "echo hello")
        print(f"    执行 Shell: {command}")
        return TaskResult(True, f"命令 '{command}' 执行完成", 1.2)


class HttpExecutor(TaskExecutor):
    """HTTP 请求执行策略"""

    def execute(self, task_id: str, params: dict) -> TaskResult:
        url = params.get("url", "https://example.com")
        method = params.get("method", "GET")
        print(f"    HTTP {method} {url}")
        return TaskResult(True, f"请求 {url} 成功", 0.5, {"status_code": 200})


class PythonExecutor(TaskExecutor):
    """Python 函数调用执行策略"""

    def execute(self, task_id: str, params: dict) -> TaskResult:
        func_name = params.get("func_name", "unknown")
        print(f"    调用 Python 函数: {func_name}")
        return TaskResult(True, f"函数 {func_name} 执行成功", 0.1)


# ---------- 任务与任务构建器（建造者模式）----------
class Task:
    """任务实体，承载任务的所有元信息和运行时状态"""

    def __init__(
        self,
        task_id: str,
        executor_type: str,
        params: dict,
        priority: Priority = Priority.MEDIUM,
        max_retries: int = 0,
    ):
        self.id = task_id
        self.executor_type = executor_type  # 对应已注册的执行器名称
        self.params = params
        self.priority = priority
        self.max_retries = max_retries
        self.status = TaskStatus.PENDING  # 初始状态为待执行
        self.retries = 0  # 当前已重试次数
        self.result: Optional[TaskResult] = None  # 执行完成后填充


class TaskBuilder:
    """
    任务构建器（建造者模式）
    每个 setter 返回 self 实现链式调用：TaskBuilder("id").executor("shell").build()
    """

    def __init__(self, task_id: str):
        self._id = task_id
        self._executor_type = "shell"  # 默认执行器
        self._params = {}
        self._priority = Priority.MEDIUM
        self._max_retries = 0

    def executor(self, executor_type: str):
        self._executor_type = executor_type
        return self  # 返回 self 支持链式调用

    def params(self, **kwargs):
        self._params = kwargs
        return self

    def priority(self, p: Priority):
        self._priority = p
        return self

    def retries(self, n: int):
        self._max_retries = n
        return self

    def build(self) -> Task:
        """终结方法：收集所有配置，构建并返回 Task 实例"""
        return Task(
            task_id=self._id,
            executor_type=self._executor_type,
            params=self._params,
            priority=self._priority,
            max_retries=self._max_retries,
        )


# ---------- 调度器（核心协调者）----------
class TaskScheduler:
    """
    任务调度器 —— 系统的核心协调者
    通过组合 EventBus 和 TaskExecutor 来协调各组件（组合优于继承）
    """

    def __init__(self):
        self._executors: dict[str, TaskExecutor] = {}  # 执行器注册表
        self._tasks: dict[str, Task] = {}  # 任务注册表
        self._event_bus = EventBus()  # 内部事件总线（组合关系）

    def register_executor(self, name: str, executor: TaskExecutor):
        """注册执行策略，name 与 Task.executor_type 对应"""
        self._executors[name] = executor

    def subscribe(self, event_type: str, listener: EventListener):
        """代理 EventBus 的订阅，对外隐藏内部实现"""
        self._event_bus.subscribe(event_type, listener)

    def unsubscribe(self, event_type: str, listener: EventListener):
        self._event_bus.unsubscribe(event_type, listener)

    def submit(self, task: Task):
        """提交任务到调度队列，并发布 task.submitted 事件"""
        self._tasks[task.id] = task
        self._event_bus.publish(
            "task.submitted", task.id, {"priority": task.priority.name}
        )

    def run_task(self, task_id: str):
        """执行单个任务，含失败重试逻辑"""
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"任务 {task_id} 不存在")

        # 根据任务的 executor_type 查找对应的执行策略
        executor = self._executors.get(task.executor_type)
        if not executor:
            raise ValueError(f"未知执行器：{task.executor_type}")

        task.status = TaskStatus.RUNNING
        self._event_bus.publish("task.started", task_id, {})

        # 委托给具体的执行器执行（策略模式的调用点）
        try:
            task.result = executor.execute(task.id, task.params)
            task.status = (
                TaskStatus.SUCCESS if task.result.success else TaskStatus.FAILED
            )
        except Exception as e:
            task.result = TaskResult(False, str(e))
            task.status = TaskStatus.FAILED

        # 失败重试：未超过最大重试次数时，重置状态并递归重试
        if task.status == TaskStatus.FAILED and task.retries < task.max_retries:
            task.retries += 1
            task.status = TaskStatus.PENDING
            self._event_bus.publish("task.retry", task_id, {"attempt": task.retries})
            self.run_task(task_id)  # 递归重试（注意：大量重试时有栈溢出风险）
        else:
            # 最终结果事件，事件名形如 task.成功 / task.失败
            self._event_bus.publish(
                f"task.{task.status.value}",
                task.id,
                {"message": task.result.message} if task.result else {},
            )

    def run_all(self):
        """按优先级从高到低执行所有待执行任务"""
        # reverse=True 使 CRITICAL(4) > HIGH(3) > MEDIUM(2) > LOW(1)
        sorted_task = sorted(
            self._tasks.values(), key=lambda t: t.priority.value, reverse=True
        )
        for task in sorted_task:
            if task.status == TaskStatus.PENDING:
                self.run_task(task.id)

    def get_report(self) -> dict:
        """生成任务执行统计报告，使用生成器表达式 + sum 统计各状态数量"""
        return {
            "总任务数": len(self._tasks),
            "成功": sum(
                1 for t in self._tasks.values() if t.status == TaskStatus.SUCCESS
            ),
            "失败": sum(
                1 for t in self._tasks.values() if t.status == TaskStatus.FAILED
            ),
            "待执行": sum(
                1 for t in self._tasks.values() if t.status == TaskStatus.PENDING
            ),
        }


# ---------- 运行演示 ----------
if __name__ == "__main__":
    print("=" * 60)
    print("任务调度系统演示")
    print("=" * 60)

    # 创建调度器
    scheduler = TaskScheduler()

    # 注册执行器（策略模式）
    scheduler.register_executor("shell", ShellExecutor())
    scheduler.register_executor("http", HttpExecutor())
    scheduler.register_executor("python", PythonExecutor())

    # 订阅事件
    logger = ConsoleLogger()
    metrics = MetricsCollector()
    scheduler.subscribe("task.submitted", logger)
    scheduler.subscribe("task.started", logger)
    scheduler.subscribe("task.成功", logger)
    scheduler.subscribe("task.失败", logger)
    scheduler.subscribe("task.submitted", metrics)
    scheduler.subscribe("task.成功", metrics)

    # 构建并提交任务（建造者模式）
    t1 = (
        TaskBuilder("backup-db")
        .executor("shell")
        .params(command="pg_dump mydb > backup.sql")
        .priority(Priority.HIGH)
        .retries(2)
        .build()
    )

    t2 = (
        TaskBuilder("health-check")
        .executor("http")
        .params(url="https://api.example.com/health", method="GET")
        .priority(Priority.CRITICAL)
        .build()
    )

    t3 = (
        TaskBuilder("send-report")
        .executor("python")
        .params(function="generate_daily_report")
        .priority(Priority.LOW)
        .build()
    )

    scheduler.submit(t1)
    scheduler.submit(t2)
    scheduler.submit(t3)

    print("\n--- 开始执行 ---")
    scheduler.run_all()

    print("\n--- 执行报告 ---")
    for k, v in scheduler.get_report().items():
        print(f"    {k}: {v}")

    print(f"事件统计：{metrics.counts}")
