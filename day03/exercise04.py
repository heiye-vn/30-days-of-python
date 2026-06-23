# 检查 7 除以 3 的 Floor 除法是否等于 2.7 的整数转换值

# 1. 计算 Floor 除法
floor_div_result = 7 // 3

# 2. 计算整数转换值
int_convert_result = int(2.7)

# 3. 比较并输出结果
is_equal = floor_div_result == int_convert_result

print(f"7 // 3 的结果是: {floor_div_result}")
print(f"int(2.7) 的结果是: {int_convert_result}")
print(f"两者是否相等: {is_equal}")

# 检查 '10' 的类型是否等于 10 的类型。
print(type("10") is type(10))

# 检查 int('9.8') 是否等于 10
print(int(float("9.8")) == 10)  # int() 只能解析整数数字的字符串
