"""
任务调度系统
涉及：SOLID 原则、策略模式、观察者模式、建造者模式、组合优于继承
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Protocol


# ---------- 枚举与数据类 ----------
class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class TaskStatus(Enum):
    PENDING = "待执行"
    RUNNING = "执行中"
    SUCCESS = "成功"
    FAILED = "失败"
    CANCELLED = "已取消"


@dataclass
class TaskResult:
    success: bool
    message: str
    duration_seconds: float = 0.0
    data: dict = field(default_factory=dict)


# ---------- 事件系统（观察者模式）----------
class EventListener(Protocol):
    def on_event(self, event_type: str, task_id: str, detail: dict): ...


class EventBus:
    def __init__(self):
        self._listeners: dict[str, list[EventListener]] = {}

    def subscribe(self, event_type: str, listener: EventListener):
        self._listeners.setdefault(event_type, []).append(listener)

    def unsubscribe(self, event_type: str, listener: EventListener):
        self._listeners.setdefault(event_type, []).remove(listener)

    def publish(self, event_type: str, task_id: str, detail: dict):
        for listener in self._listeners.get(event_type, []):
            listener.on_event(event_type, task_id, detail or {})


class ConsoleLogger:
    def on_event(self, event_type: str, task_id: str, detail: dict):  # noqa
        time = datetime.now().strftime("%H:%M:%S")
        print(f"  [{time}] [{event_type}] 任务 {task_id}: {detail}")


class MetricsCollector:
    def __init__(self):
        self.counts: dict[str, int] = {}

    def on_event(self, event_type: str, task_id: str, detail: dict):
        self.counts[event_type] = self.counts.get(event_type, 0) + 1
