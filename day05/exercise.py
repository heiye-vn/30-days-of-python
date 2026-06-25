ages = [19, 22, 19, 24, 20, 25, 26, 24, 25, 24]

# 对列表进行排序，并找出最大和最小年龄
ages.sort()
# print(ages)
print("最小年龄是：", ages[0])
print("最大年龄是：", ages[-1])
# print(f"用 max() 获取最大年龄：{max(ages)}")
# print(f"用 min() 获取最小年龄：{min(ages)}")

# 将最小年龄和最大年龄再次添加到列表中
min_age = min(ages)
max_age = max(ages)
ages.append(min_age)
ages.append(max_age)
# print(ages)

# 找到年龄中位数（一个中间项或两个中间项除以二）
# print(len(ages))
ages.sort()  # 中位数必须先排序
print(ages)

n = len(ages)
if n % 2 == 0:
    median_age = (ages[n // 2 - 1] + ages[n // 2]) / 2
else:
    median_age = ages[n // 2]
print(f"年龄中位数是：{median_age}")

# 找到平均年龄（所有项的总和除以它们的数量）
average_age = sum(ages) / len(ages)
print(f"平均年龄是：{average_age}")

# 找到年龄范围（最大减去最小）
age_range = max(ages) - min(ages)
print(f"年龄范围是：{age_range}")

print(abs(min_age - average_age) > abs(max_age - average_age))
