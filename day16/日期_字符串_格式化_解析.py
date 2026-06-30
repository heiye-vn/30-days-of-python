from datetime import datetime

now = datetime.now()

# datetime → 字符串（格式化）
s = now.strftime("%Y-%m-%d %H:%M:%S")
s2 = now.strftime("%Y年%m月%d日")
print(s)
print(s2)
print(type(s))

# 字符串 → datetime（解析）
dt = datetime.strptime("2024-01-15 14:30", "%Y-%m-%d %H:%M")
print(dt)
print(type(dt))
