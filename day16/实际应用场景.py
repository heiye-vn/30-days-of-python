"""
日期/时间在项目中的实际应用场景
"""
from datetime import time, datetime

"""
1. 判断是否在营业时间内
"""
OPEN = time(9, 0)
CLOSE = time(21, 30)


def is_open(now: time = None) -> bool:  # noqa
    now = now or datetime.now().time()
    return OPEN <= now <= CLOSE


print(f"22:00 还在营业吗？ {is_open(time(22, 0))}")
print(f"11: 30 应该营业了吧？ {is_open(time(11, 30))}")
