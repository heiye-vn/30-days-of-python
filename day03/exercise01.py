# 练习

# 编写一个脚本，提示用户输入三角形的底和高，并计算这个三角形的面积（面积 = 0.5 x b x h）
try:
    triangle_end = input('请输入三角形的底：')
    triangle_height = input('请输入三角形的高：')

    if not triangle_end or not triangle_height:
        print("错误：输入不能为空！")
    else:
        base = float(triangle_end)
        height = float(triangle_height)

        if base <= 0 or height <= 0:
            print("错误：底和高必须为正数！")
        else:
            area = 0.5 * base * height
            print(f"三角形面积为：{area}")
except ValueError:
    print("错误：请输入有效的数字！")
