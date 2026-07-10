"""
dictConfig（推荐中大型项目）
把配置放到字典里，和代码解耦，可直接读 YAML / JSON 文件
"""

import logging.config
from pathlib import Path

import yaml

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # ??💡💡，不要禁用已有的 logger
    "formatters": {
        "simple": {"format": "%(asctime)s [%(levelname)s] %(message)s"},
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "logs/app.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "myapp": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        }
    },
    "root": {"level": "WARNING", "handlers": ["console"]},
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("myapp")
logger.info("Logger 配置完成（dictConfig），开始运行")


"""
或者从 YAML 文件加载配置
"""
# config_path = Path("config/logging.yaml")
# with open(config_path, "r", encoding="utf-8") as f:
#     config = yaml.safe_load(f)
#
# logging.config.dictConfig(config)
