"""
综合应用：打包、解包、展开与异常处理
"""

import json
import logging

"""
1. 构建通用的安全调用器
"""
logger = logging.getLogger(__name__)


def safe_call(func, *args, default=None, **kwargs):
    """
    安全地调用函数，捕获所有异常并返回默认值。
    综合运用了 *args（打包位置参数）和 **kwargs（打包关键字参数）。
    """
    try:
        return func(*args, **kwargs)  # 展开参数
    except Exception as e:
        logger.warning(f"调用 {func.__name__} 失败：{e}")
        return default


# 安全解析 JSON
result = safe_call(json.loads, '{"name": "Alice"}')
# print(result)

# bad_result = safe_call(json.loads, "not a json", default={})
# print(bad_result)

# 安全文件读取
# content = safe_call(open, "nonexistent.txt", default="", mode="r")
# print(content)


"""
2. 实现一个灵活的配置管理器
"""


class ConfigManager:
    def __init__(self, **defaults):
        self._config = {**defaults}  # 展开并复制默认配置

    def update(self, **overrides):
        """批量更新"""
        self._config = {**self._config, **overrides}

    def get(self, key, default=None):
        try:
            return self._config[key]
        except KeyError:
            if default is not None:
                return default
            raise KeyError(f"配置项 '{key} 不存在且未提供默认值'")

    def export(self):
        return {**self._config}  # 返回副本


# 使用
config = ConfigManager(
    database_url="postgresql://localhost:5432/mydb",
    redis_url="redis://localhost:6379",
    debug=False,
    log_level="INFO",
)

# 根据环境变量覆盖
env_overrides = {"debug": True, "log_level": "DEBUG"}
config.update(**env_overrides)
print(config.export())
