num = 7

result = "偶数" if num % 2 == 0 else "奇数"
# print(result)

username = "admin"
password = "123456"

loginMessage = "登录成功" if username == "admin" and password == "123456" else "用户名或密码错误"
# print(loginMessage)

'''
判断闰年：能被 400 整除或者能被 4 整除但不能被 100 整除
'''
year = 2024
year_result = "闰年" if year % 400 == 0 or (year % 4 == 0 and year % 100 != 0) else "不是闰年"
# print(year_result)


# 判断正负数：输入一个数字，判断它是正数、负数还是 0。
# num = int(input('请输入一个数字：'))
# if num > 0:
#     print('正数')
# elif num < 0:
#     print('负数')
# else:
#     print('零')

# 判断成绩
# score = int(input("请输入成绩："))
#
# if score >= 90:
#     print("A")
# elif score >= 80:
#     print("B")
# elif score >= 70:
#     print("C")
# elif score >= 60:
#     print("D")
# else:
#     print("E")

# 判断是否可以买票：年龄大于等于 18，且有身份证，才可以买票
age = int(input("请输入年龄："))
has_id = input("是否有身份证（yes/no）：")

if age >= 18 and has_id == "yes":
    print("可以买票")
else:
    print("不可以买票")
