TAX_RATE = 0.13  # 增值税率


def get_total_price(price, discount=0):
    """计算折后含税总价"""
    discounted_price = price * (1 - discount)
    return discounted_price * (1 + TAX_RATE)


print("这是模块被引入时会直接运行的代码")

# 只有直接执行该文件时才会执行，当该文件会被……引入执行
if __name__ == "__main__":
    import math  # 导入内置 math 模块以使用 isclose

    print("--- 正在运行 price_tools 模块的内部测试 ---")
    # 由于浮点数精度限制，100 * 1.13 在计算机中为 112.99999999999999，不能用 == 直接比较
    assert math.isclose(get_total_price(100), 113.0)
    print("测试通过！")
