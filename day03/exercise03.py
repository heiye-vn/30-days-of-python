# 偶数可以被 2 整除,余数为零。如何使用 Python 检查一个数字是偶数还是奇数
try:
    num = input('请输入数字：')

    if not num:
        print("错误：输入不能为空！")
    else:
        number = float(num)

        # python 在进行数字比较时会转换为相同类型后再比较
        # if number != int(number):
        if not number.is_integer():
            print("错误：奇偶性只对整数有意义！")
        elif number <= 0:
            print("错误：请输入正整数！")
        else:
            if int(number) % 2 == 0:
                print("该数为偶数")
            else:
                print("该数为奇数")

except ValueError:
    print("错误：请输入有效的数字！")
