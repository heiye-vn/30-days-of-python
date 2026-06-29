def calculate_bmi(weight, height):
    """
    计算 BMI 指数

    参数:
        weight (float): 体重（kg）
        height (float): 身高（m）

    返回:
        float: BMI 指数
    """
    return weight / (height ** 2)


# print(calculate_bmi.__doc__)
help(calculate_bmi)
