"""
日期/时间在项目中的实际应用场景
"""

import time as time_module
from datetime import datetime, time, timedelta, timezone

"""
1. 判断是否在营业时间内
"""
OPEN = time(9, 0)
CLOSE = time(21, 30)


def is_open(now: time = None) -> bool:  # noqa
    now = now or datetime.now().time()
    return OPEN <= now <= CLOSE


# print(f"22:00 还在营业吗？ {is_open(time(22, 0))}")
# print(f"11: 30 应该营业了吧？ {is_open(time(11, 30))}")


"""
场景一：日记记录与数据库存储

在分布式系统或 Web 接口中，存储时间时必须存为 UTC 时间或带时区的绝对时间，展示时再转换为本地时间
"""


def generate_log_meta():
    """生成标准格式日志元数据"""
    # 存入数据库：永远使用 UTC 时间且带有时区标记（Aware）
    utc_now = datetime.now(timezone.utc)

    # 格式化输出为 ISO 8601 标准字符串，便于第三方日志系统分析
    log_format = utc_now.isoformat()

    return {"timestamp_utc": log_format, "created_at_db": utc_now}


log_meta = generate_log_meta()
# print(f"日志时间：{log_meta['timestamp_utc']}")
# print(f"数据库存储时间：{log_meta['created_at_db']}")


"""
场景二：Token 过期与促销倒计时计算

利用 timedelta 自动计算未来或过去的某一时间点，并判断当前是否超时
"""


def generate_jwt_expiration(expire_minutes=30):
    """计算 Token 过期时间"""
    now = datetime.now(timezone.utc)
    expire_at = now + timedelta(minutes=expire_minutes)
    return expire_at


def is_token_expired(expire_at):
    """判断 Token 是否已过期"""
    # 必须保持同为 Aware datetime 比较，否则会抛出 TypeError
    return datetime.now(timezone.utc) > expire_at


token_expire_time = generate_jwt_expiration()
# print(f"Token 将在 {token_expire_time} 过期")
# print(f"是否已过期：{is_token_expired(token_expire_time)}")


"""
场景三：跨国业务中的时区转换

从外部 API 拿到了带有特定时区的字符串时间，需要转换成本地时区时间
"""
# 1. 解析美国纽约时间的字符串（EST 标准时间 UTC-5，夏令时 EDT 为 UTC-4）
ny_time_str = "2026-06-30 08:30:00 -0500"
# %z 可以解析 -0500 或 -0800 格式的时区偏移
ny_dt = datetime.strptime(ny_time_str, "%Y-%m-%d %H:%M:%S %z")
# print(f"纽约时间（Aware）：{ny_dt}")

# 2. 将其转换为北京时间（UTC+8）
tz_beijing = timezone(timedelta(hours=8))
beijing_dt = ny_dt.astimezone(tz_beijing)
# print(f"对应的北京时间：{beijing_dt}")


"""
场景四：优化的代码执行时间耗时分析

在开发中，若要快速诊断一段逻辑的耗时情况，time.perf_counter() 是最佳选择， 它提供了系统级的最高分辨率时钟
"""


def process_large_data():
    # 模拟数据耗时处理
    time_module.sleep(0.8)


# 获取高精度起点
start_time = time_module.perf_counter()

process_large_data()

# 计算耗时
end_time = time_module.perf_counter()
execution_time = end_time - start_time
print(f"数据处理耗时：{execution_time:.6f} 秒")
