# 编写一个脚本，提示用户输入三角形的边 a、边 b 和边 c。计算三角形的周长（周长 = a + b + c）
try:
    triangle_edge_a = input('输入三角形边 a：')
    triangle_edge_b = input('输入三角形边 b：')
    triangle_edge_c = input('输入三角形边 c：')

    if not triangle_edge_a or not triangle_edge_b or not triangle_edge_c:
        print("错误：输入不能为空！")
    else:
        edgeA = float(triangle_edge_a)
        edgeB = float(triangle_edge_b)
        edgeC = float(triangle_edge_c)

        if edgeA <= 0 or edgeB <= 0 or edgeC <= 0:
            print("错误：三角形边必须为正数！")
        # 三角形有效性验证（任意两边之和必须大于第三边，无效情况则是小于等于）
        if (edgeA + edgeB <= edgeC) or (edgeA + edgeC <= edgeB) or (edgeB + edgeC <= edgeA):
            print("错误：这三条边无法构成三角形！")
        else:
            perimeter = edgeA + edgeB + edgeC
            print(f"三角形周长为：{perimeter}")
except ValueError:
    print("错误：请输入有效的数字！")
