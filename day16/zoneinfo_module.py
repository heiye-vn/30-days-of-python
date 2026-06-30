from datetime import datetime
from zoneinfo import ZoneInfo

# 获取带时区的当前时间（windows 系统需要安装 tzdata 第三方包）
dt_shanghai = datetime.now(ZoneInfo("Asia/Shanghai"))
print(f"上海时间: {dt_shanghai}")

# 跨时区转换
dt_new_york = dt_shanghai.astimezone(ZoneInfo("America/New_York"))
print(f"纽约时间: {dt_new_york}")

# 东京时间
dt_tokyo = dt_shanghai.astimezone(ZoneInfo("Asia/Tokyo"))
print(f"东京时间: {dt_tokyo}")
