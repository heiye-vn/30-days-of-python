from datetime import date, datetime, timedelta
from typing import Dict, List, Union
from zoneinfo import ZoneInfo

"""
练习 1:
使用 `zoneinfo` 编写一个世界时钟函数，同时显示北京、纽约、伦敦、东京四个城市的当前时间
"""


def get_world_clock() -> Dict[str, str]:
    """
    获取北京、纽约、伦敦、东京四个城市的当前时间
    返回包含城市名称和对应格式化时间字符串的字典
    """
    cities = {
        "北京": "Asia/Shanghai",
        "纽约": "America/New_York",
        "伦敦": "Europe/London",
        "东京": "Asia/Tokyo",
    }
    world_time = {}
    # 获取当前的 UTC 时间，确保所有城市的时间是完全同步的
    now_utc = datetime.now(ZoneInfo("UTC"))
    for city, tz_name in cities.items():  # noqa
        # 将 UTC 时间转换到目标时区
        city_time = now_utc.astimezone(ZoneInfo(tz_name))
        world_time[city] = city_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    return world_time


"""
练习 2:
创建一个日历生成函数，接收开始和结束日期，返回一个包含该日期范围内的所有日期的列表。
"""


def generate_date_range(
    start_date: Union[str, date], end_date: Union[str, date]
) -> List[str]:
    """
    生成接收的开始和结束日期范围内的所有日期的列表 (包含首尾日期)

    :param start_date: 开始日期，支持 "YYYY-MM-DD" 格式字符串或 datetime.date 对象
    :param end_date: 结束日期，支持 "YYYY-MM-DD" 格式字符串或 datetime.date 对象
    :return: 包含所有日期字符串的列表 (格式 "YYYY-MM-DD")
    """
    # 转换开始日期
    if isinstance(start_date, str):
        start = datetime.strptime(start_date, "%Y-%m-%d").date()  # noqa
    elif isinstance(start_date, datetime):
        start = start_date.date()  # noqa
    else:
        start = start_date  # noqa

    # 转换结束日期
    if isinstance(end_date, str):
        end = datetime.strptime(end_date, "%Y-%m-%d").date()  # noqa
    elif isinstance(end_date, datetime):
        end = end_date.date()  # noqa
    else:
        end = end_date  # noqa

    if start > end:
        return []

    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return dates


# --- 验证测试 ---
if __name__ == "__main__":
    print("--- 1. 世界时钟 (World Clock) ---")
    clock = get_world_clock()
    for city, time_str in clock.items():
        print(f"{city:<4}: {time_str}")

    print("\n--- 2. 日历范围生成 (Calendar Generator) ---")
    start = "2026-06-25"
    end = "2026-07-02"
    date_list = generate_date_range(start, end)
    print(f"从 {start} 到 {end} 的日期列表:")
    for d in date_list:
        print(d)
