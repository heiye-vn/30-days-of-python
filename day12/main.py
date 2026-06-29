# 使用 import 导入整个模块，通过 moduleName.属性/方法 方式访问模块中的属性和方法
# import price_tools

# 使用 from ... import ... 方式导入具体的属性或方法，调用时只需使用方法名或属性名即可
from price_tools import TAX_RATE, get_total_price

print(get_total_price.__doc__)

final_price = get_total_price(100, discount=0.2)
print(f"最终价格：{final_price}")
print(f"当前税率：{TAX_RATE}")
