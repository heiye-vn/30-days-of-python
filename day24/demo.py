"""
Python 多目的地日志演示
=======================
演示将日志同时输出到：控制台、文件、邮件（模拟）

运行方式:
  python logging_multi_destination.py

邮件部分使用自定义 Handler 模拟发送，无需真实邮箱即可看到完整流程。
如需接入真实邮箱，替换为 logging.handlers.SMTPHandler 即可（见底部说明）。
"""

import logging
import logging.handlers
import time
from datetime import datetime
from pathlib import Path

# ============================================================
# 日志目录
# ============================================================
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


# ============================================================
# 自定义邮件 Handler（模拟发送，实际打印到控制台）
# ============================================================
class MockEmailHandler(logging.Handler):
    """
    模拟邮件发送的 Handler。
    只处理 ERROR 及以上级别的日志，将内容格式化为邮件样式输出。
    生产环境中替换为 logging.handlers.SMTPHandler 即可真正发送邮件。
    """

    def __init__(self, fromaddr, toaddrs, subject, smtp_host="smtp.example.com"):
        super().__init__()
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs if isinstance(toaddrs, list) else [toaddrs]
        self.subject = subject
        self.smtp_host = smtp_host
        self._sent_count = 0

    def emit(self, record):
        try:
            # 格式化日志记录
            msg = self.format(record)

            self._sent_count += 1
            separator = "~" * 50
            print(f"\n{separator}")
            print(f"  [模拟邮件 #{self._sent_count}] 已发送!")
            print(f"  From:    {self.fromaddr}")
            print(f"  To:      {', '.join(self.toaddrs)}")
            print(f"  Subject: {self.subject}")
            print(f"  Time:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(separator)
            # 打印邮件正文（缩进显示）
            for line in msg.split("\n"):
                print(f"  | {line}")
            print(f"{separator}\n")

        except Exception:  # noqa
            self.handleError(record)


# ============================================================
# Logger 配置
# ============================================================
def setup_logger() -> logging.Logger:
    """
    配置一个同时输出到三个目的地的 logger:
      1. 控制台 -- INFO 及以上, 简洁格式
      2. 文件   -- DEBUG 及以上, 详细格式, 按大小滚动
      3. 邮件   -- ERROR 及以上, 带完整上下文信息
    """
    logger = logging.getLogger("myapp")
    logger.setLevel(logging.DEBUG)  # logger 级别设为最低, 让 handler 各自控制

    # ---------- 格式定义 ----------
    console_fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S"
    )
    file_fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    email_fmt = logging.Formatter(
        "时间: %(asctime)s\n"
        "级别: %(levelname)s\n"
        "模块: %(name)s\n"
        "函数: %(funcName)s (行 %(lineno)d)\n"
        "进程: %(process)d\n"
        "----------------------------\n"
        "%(message)s\n"
        "%(exc_info)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ---------- 1. 控制台 Handler ----------
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # 控制台只显示 INFO+
    console_handler.setFormatter(console_fmt)

    # ---------- 2. 文件 Handler（按大小滚动）----------
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=5 * 1024 * 1024,  # 单文件最大 5 MB
        backupCount=3,  # 保留 3 个历史文件
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)  # 文件记录所有 DEBUG+ 日志
    file_handler.setFormatter(file_fmt)

    # ---------- 3. 邮件 Handler（模拟）----------
    # 生产环境替换为:
    # mail_handler = logging.handlers.SMTPHandler(
    #     mailhost=("smtp.company.com", 587),
    #     fromaddr="alert@company.com",
    #     toaddrs=["admin@company.com"],
    #     subject="[ERROR] Application Alert",
    #     credentials=("user", "password"),
    #     secure=(),   # 启用 TLS
    # )
    mail_handler = MockEmailHandler(
        fromaddr="app-alert@company.com",
        toaddrs=["admin@company.com", "ops-team@company.com"],
        subject="[ALERT] Application Error Alert",
    )
    mail_handler.setLevel(logging.ERROR)  # 只有 ERROR+ 才发邮件
    mail_handler.setFormatter(email_fmt)

    # ---------- 组装到 logger ----------
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(mail_handler)

    return logger


# ============================================================
# 模拟业务场景
# ============================================================
def process_order(logger, order_id, user_id, items):
    """模拟订单处理，演示不同级别的日志输出"""

    logger.info(
        "Order %s: start processing, user=%s, items=%d", order_id, user_id, len(items)
    )

    # DEBUG: 详细的内部状态
    logger.debug(
        "Order %s: inventory check - SKU counts: %s",
        order_id,
        {item: 100 - i * 10 for i, item in enumerate(items)},
    )

    # INFO: 关键业务节点
    logger.info(
        "Order %s: payment authorized, amount=%.2f", order_id, len(items) * 199.0
    )

    # WARNING: 异常但可恢复
    if len(items) > 2:
        logger.warning(
            "Order %s: large order detected, may need manual review", order_id
        )

    return True


def process_payment(logger, order_id):
    """模拟支付处理，演示 ERROR 级别日志"""

    logger.info("Payment gateway: connecting for order %s ...", order_id)

    try:
        # 模拟支付网关连接失败
        raise ConnectionError(
            "Connection to payment gateway (pay.example.com:443) timed out after 30s"
        )
    except ConnectionError as e:
        # exc_info=True 会自动附加完整的异常堆栈
        logger.error("Payment failed for order %s: %s", order_id, e, exc_info=True)
        raise


def check_system_health(logger):
    """模拟系统健康检查，演示 CRITICAL 级别日志"""

    logger.info("System health check: starting...")
    logger.debug("Health check: CPU=45%%, MEM=72%%, DISK=89%%")

    # 模拟数据库故障
    try:
        raise RuntimeError(
            "All database replicas are down! Primary and standby unreachable."
        )
    except RuntimeError as e:
        logger.critical("SYSTEM FAILURE: %s", e, exc_info=True)


# ============================================================
# 主入口
# ============================================================
def main():
    print("=" * 58)
    print("   Python Logging Demo - Multi-Destination")
    print("=" * 58)
    print()
    print("  Destinations configured:")
    print("    [1] Console  <-- INFO and above")
    print("    [2] File     <-- DEBUG and above  (logs/app.log)")
    print("    [3] Email    <-- ERROR and above  (mock)")
    print()
    print("=" * 58)
    print()

    # 配置 logger
    logger = setup_logger()

    # ---- 场景 1: 正常订单处理 ----
    print("[Scene 1] Normal order processing")
    print("-" * 40)
    process_order(logger, "ORD-20240115-001", "user_2048", ["SKU-A", "SKU-B", "SKU-C"])
    print()
    time.sleep(0.3)

    # ---- 场景 2: 支付失败（ERROR -> 触发邮件）----
    print("[Scene 2] Payment failure (triggers email)")
    print("-" * 40)
    try:
        process_payment(logger, "ORD-20240115-002")
    except ConnectionError:
        logger.info("Fallback: queued order ORD-20240115-002 for retry")
    print()
    time.sleep(0.3)

    # ---- 场景 3: 系统故障（CRITICAL -> 触发邮件）----
    print("[Scene 3] System failure (triggers email)")
    print("-" * 40)
    check_system_health(logger)
    print()
    time.sleep(0.5)

    # ---- 展示日志文件内容 ----
    log_file = LOG_DIR / "app.log"
    if log_file.exists():
        print()
        print("=" * 58)
        print(f"  Log file content: {log_file}")
        print("=" * 58)
        content = log_file.read_text(encoding="utf-8")
        # Windows console may not support all UTF-8 chars
        try:
            print(content)
        except UnicodeEncodeError:
            print(content.encode("ascii", errors="replace").decode("ascii"))
        print("=" * 58)

    print("\nDemo complete.")


if __name__ == "__main__":
    main()
