"""
calendar 模块：主要用于日历生成和日期判断
"""

import calendar
from datetime import date

# 判断闰年
# print(f"2026 年是闰年吗？ {calendar.isleap(2026)}")
# print(f"2028 年是闰年吗？ {calendar.isleap(2028)}")

# 获取某月的天数：返回改约第一天是星期几，该月总天数
week_list = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
weekday, days = calendar.monthrange(2026, 7)
# print(f"2026 年 7 月有 {days} 天，第一天是: {week_list[weekday]}")

# print(calendar.monthcalendar(2026, 6))  # 返回一个列表，表示 2026 年 6 月的日历


# 获取本月第一天/最后一天
today = date.today()
first_day = today.replace(day=1)
last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])

# print(f"本月第一天是：{first_day}")
# print(f"本月最后一天是：{last_day}")


# 打印某月日历
calendar.prmonth(2026, 7)
print('==' * 20)
print(calendar.month(2026, 6))
