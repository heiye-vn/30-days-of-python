"""
三方模块：arrow、pendulum
"""

import arrow
import pendulum

"""
arrow 示例
"""
# 获取当前时间并转化为本地时间
now = arrow.now("Asia/Shanghai")
# 时间推移与人性化输出
past = now.shift(hours=-3)
# print(past.humanize(locale="zh-CN"))
# print(past.humanize(locale="en-US"))
# print(past.humanize(locale="ja-JP"))
# print(past.humanize(locale="ko-KR"))
# print(past.humanize(locale="ru-RU"))
# print(past.humanize(locale="fr-FR"))
# print(past.humanize(locale="de-DE"))
# print(now.humanize(locale="zh"))  # "刚刚"
# print(now.shift(days=3).format("YYYY-MM-DD"))
# print(arrow.get("2026-06-30").to("UTC"))

"""
pendulum 示例
"""
# 优雅的时区初始化
# dt = pendulum.now("Europe/Paris")
# print(dt.timezone_name)

# 精确地跨时区转换
# dt_sh = dt.in_timezone('Asia/Shanghai')
# print(dt_sh.to_date_string())

dt = pendulum.now("Asia/Shanghai")
print(dt.add(months=2))
print(dt.diff_for_humans())
