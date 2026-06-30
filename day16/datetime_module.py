"""
datetime 模块核心类

date：只含年月日（无时间）
time：只含时分秒（无日期）
datetime：日期+时间的组合（最常用）
timedelta：表示时间间隔（用于日期运算
timezone：时区信息
"""
from datetime import date, time, datetime, timezone, timedelta

"""
date 类
"""
# 获取今天的日期
today = date.today()
# print(f"今天日期：{today}")
# 获取 today 的属性/方法
# print(dir(today))
# print(f"年: {today.year}, 月: {today.month}, 日: {today.day}")

# 创建指定日期
specific_date = date(2026, 10, 1)
# print(f"国庆节：{specific_date}")


"""
time 类
"""
# 创建时间对象（时、分、秒、微秒）
# t = time(14, 30, 45, 500)
# print(f"指定时间: {t}")
# print(f"时: {t.hour}, 分: {t.minute}, 秒: {t.second}")


"""
datetime 类，日期+时间的组合，最常用
"""
# 获取当前本地时间（Naive）
now_naive = datetime.now()
# print(f"本地 Naive 时间：{now_naive}")

# 获取当前 UTC 时间（Aware，推荐方式）
now_utc = datetime.now(timezone.utc)  # utcnow() 方法已弃用，推荐使用 now() 并传入 timezone.utc
# print(f"UTC Aware 时间：{now_utc}")  # 与本地时间相比，UTC 时间少了 8 小时

# 指定时间
dt = datetime(2026, 10, 1, 14, 30, 55)
# print(f"指定时间：{dt}")

# 拼接日期与时间
d = date(2026, 6, 30)
t = time(9, 30, 0)
combined = datetime.combine(d, t)
# print(f"拼接后的 datetime：{combined}")


"""
timedelta 类，表示两个日期或时间之间的时间差，主要用于日期的加减运算
核心参数：weeks=, days=, hours=, minutes=, seconds=, microseconds=, milliseconds=。
"""
now = datetime.now()
# print(f"当前时间：{now}")

# 加 7 天
next_week = now + timedelta(days=7)
# print(f"一周后：{next_week}")

# 减 3 小时
past_three_hours = now - timedelta(hours=3)
# print(f"三小时前：{past_three_hours}")

# 计算两个日期之间的差值
# delta_time = next_week - now
delta_time = datetime(2026, 10, 3) - now
# print(f"相差天数：{delta_time.days} 天，相差秒数：{delta_time.total_seconds()} 秒")


"""
timezone，声明时区信息
"""
# 创建北京时间（东八区、UCT+8）
tz_bj = timezone(timedelta(hours=8))
# 获取带北京时区的当前时间
now_bj = datetime.now(tz_bj)
print(f"当前北京时间：{now_bj}")
