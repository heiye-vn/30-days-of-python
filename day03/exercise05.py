# 编写一个脚本，提示用户输入年数。计算一个人可以活多少秒。假设一个人可以活一百年

# 定义常数（一年的秒数：365天 * 24小时 * 60分钟 * 60秒）
SECONDS_PER_YEAR = 365 * 24 * 60 * 60

try:
    # 提示用户输入，并使用 float 支持小数年数（如 29.5）
    year_input = input("请输入你已经活了多少年：")
    year = float(year_input)
    
    # 检查输入的合理性（限制在 0 到 100 年之间）
    if year < 0 or year > 100:
        print("请输入一个介于 0 到 100 之间的合理年数。")
    else:
        seconds = year * SECONDS_PER_YEAR
        # 如果是整数年，输出时去掉小数点
        if seconds.is_integer():
            print(f"你已经活了 {int(seconds)} 秒")
        else:
            print(f"你已经活了 {seconds:.2f} 秒")

except ValueError:
    print("输入错误！请输入一个有效的数字。")
