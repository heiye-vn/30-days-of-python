"""
代码配置（适合脚本和小项目）
"""

import logging
from logging.handlers import RotatingFileHandler


def setup_logger():
    logger = logging.getLogger("myapp")
    logger.setLevel(logging.DEBUG)

    # 控制台：INFO 及以上
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    )

    # 文件：DEBUG 及以上，按大小滚动
    file_handler = RotatingFileHandler(
        "logs/app.log", maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
        )
    )

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger


logger = setup_logger()
logger.info("Logger 配置完成，开始运行")
