"""
常用设计模式
"""

from abc import ABC, abstractmethod
from typing import Protocol

"""
1. 单例模式：一个类只有一个实例，全局共享
"""


class AppConfig:
    """应用配置，全局只需一份"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._settings = {}
        return cls._instance

    def set(self, key: str, value):
        self._settings[key] = value

    def get(self, key: str, default=None):
        return self._settings.get(key, default)


# 不管创建多少次，都是共享的一个实例对象
config1 = AppConfig()
config2 = AppConfig()
# print(config1 is config2)

config1.set("format", "YYYY-MM-DD")
# print(config2.get("format"))

# Pythonic 代替方案：用模块（.py文件）级变量也可以实现单例效果
# settings.py
_settings = {}


def set_config(key, value):
    _settings[key] = value


def get_config(key, default=None):
    return _settings.get(key, default)


"""
2. 工厂模式：定义一个创建对象的接口，让子类决定实例化哪一个类
"""


class Logger(ABC):
    @abstractmethod
    def log(self, message: str): ...


class FileLogger(Logger):
    def log(self, message: str):
        with open("app.log", "a", encoding="utf-8") as f:
            f.write(message + "\n")


class ConsoleLogger(Logger):
    def log(self, message: str):
        print(f"[LOG] {message}")


class DatabaseLogger(Logger):
    def log(self, message: str):
        print(f"[DB LOG] INSERT INTO logs VALUES ('{message}')")


# 工厂函数
def create_logger(log_type: str) -> Logger:
    loggers = {
        "file": FileLogger(),
        "console": ConsoleLogger(),
        "database": DatabaseLogger(),
    }
    if log_type not in loggers:
        raise ValueError(f"未知日志类型：{log_type}")
    return loggers[log_type]


# 使用方无需知道具体类
logger = create_logger("console")
# logger.log("应用启动")


"""
3. 装饰器模式：动态给对象添加额外功能，而不改变原始类
"""


class TextProcessor(ABC):
    @abstractmethod
    def process(self, text: str) -> str: ...


class PlainText(TextProcessor):
    def process(self, text: str) -> str:
        return text


class UpperCaseDecorator(TextProcessor):
    def __init__(self, wrapped: TextProcessor):
        self._wrapped = wrapped

    def process(self, text: str) -> str:
        return self._wrapped.process(text).upper()


class TrimDecorator(TextProcessor):
    def __init__(self, wrapped: TextProcessor):
        self._wrapped = wrapped

    def process(self, text: str) -> str:
        return self._wrapped.process(text).strip()


class ReverseDecorator(TextProcessor):
    def __init__(self, wrapped: TextProcessor):
        self._wrapped = wrapped

    def process(self, text: str) -> str:
        return self._wrapped.process(text)[::-1]


processor = PlainText()
processor = UpperCaseDecorator(processor)
processor = TrimDecorator(processor)
# processor = ReverseDecorator(processor)

result = processor.process("  hello world  ")
# print(result)


"""
4. 观察者模式
一个对象状态变化时，自动通知所有关心它的对象
"""


class Observer(Protocol):
    def update(self, event: str, data: dict): ...


class EventBus:
    """事件总线：发布-订阅"""

    def __init__(self):
        self._listeners: dict[str, list[Observer]] = {}

    def subscribe(self, event: str, observer: Observer):
        self._listeners.setdefault(event, []).append(observer)

    def unsubscribe(self, event: str, observer: Observer):
        if event in self._listeners:
            self._listeners[event].remove(observer)

    def publish(self, event: str, data=None):
        if data is None:
            data = {}
        for observer in self._listeners.get(event, []):
            observer.update(event, data)


# 观察者实现
class EmailNotifier:
    def update(self, event: str, data: dict):  # noqa
        print(f"[邮件] 事件 {event}：给用户 {data.get('user', '?')} 发送通知")


class LogRecorder:
    def update(self, event: str, data: dict):  # noqa
        print(f"[日志] 记录事件 {event}：{data}")


class MetricsCollector:
    def update(self, event: str, data: dict):  # noqa
        print(f"[指标] 统计事件 {event}")


# 使用
bus = EventBus()
# 订阅事件
bus.subscribe("user.registered", EmailNotifier())
bus.subscribe("user.registered", LogRecorder())
bus.subscribe("user.created", MetricsCollector())

# 发布事件
# bus.publish("user.registered", {"user": "张三", "email": "zs@example.com"})
