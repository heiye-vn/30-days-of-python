"""
常用的第三方验证库
"""
from pydantic import BaseModel, EmailStr, HttpUrl, Field, field_validator

"""
1. pydantic —— 数据验证和设置
"""


# 定义一个数据模型，字段类型即验证规则
class User(BaseModel):
    name: str
    # ge=0 表示值必须大于等于 0
    age: int = Field(default=0, ge=0)
    email: EmailStr  # 自动验证邮箱格式（需安装 email-validator）
    homepage: HttpUrl | None = None


# 合法数据
user1 = User(name="张三", age=25, email="zhangsan@example.com")


# print(user1)

# try:
#     bad_user = User(name="李四", age=-5, email="not-an-email")
# except Exception as e:
#     print(e)


# 自定义验证规则
class Product(BaseModel):
    name: str
    price: float | int

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("商品名称不能为空")
        return v.strip()

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("价格必须大于 0")
        return v


p_normal = Product(name="  Python 教程  ", price=49.9)
# print(p_normal.name)

# try:
#     Product(name="", price=-10)
# except Exception as e:
#     print(e)


"""
2. validators —— 轻量级验证函数集合
使用场景：快速校验单个字段、脚本中做简单的数据过滤、不想引入重型框架时的轻量验证
"""
# 验证 URL
# print(validators.url("https://www.python.org"))
# print(validators.url("not a url"))

# 验证邮箱
# print(validators.email("user@example.com"))
# print(validators.email("bad@email"))

# 验证 IP 地址
# print(validators.ipv4("192.168.1.1"))
# print(validators.ipv6("::1"))

# 验证 uuid
# print(validators.uuid("123e4567-e89b-12d3-a456-426614174000"))

# 验证信用卡号（Luhn 算法）
# print(validators.card_number("4111111111111111"))

# 在 if 语句中使用时，注意判断返回值
# result = validators.url("http://www.baidu.com")
# if result is True:  # 注意用 is True，因为 ValidationFailure 对象的布尔值也是 False
#     print("合法的 URL")
# else:
#     print(f"非法的 URL：{result}")


"""
3. email-validator —— 专业的邮箱验证
它不仅检查格式，还能验证域名是否真实存在（DNS 查询），甚至检查邮箱是否可投递
使用场景：用户注册时的邮箱验证、邮件营销系统中的地址清洗、需要确保域名真实存在的场景
"""

# 简单验证（只检查格式）
# try:
#     result = validate_email("user@example.com", check_deliverability=False)
#     print(result.normalized)
#     print(result.local_part)
#     print(result.domain)
# except EmailNotValidError as e:
#     print(f"邮箱不合法：{e}")

# 完整验证（默认会检查域名的 MX 记录）
# try:
#     result = validate_email("user@example.com")
#     print(f"合法邮箱：{result.normalized}")
# except EmailNotValidError as e:
#     print(f"邮箱不合法：{e}")

# 常见错误示例
test_emails = [
    "user@example",  # 缺少顶级域名
    "user@.com",  # 域名不合法
    "@example.com",  # 缺少用户名
    "user@domain.xyz",  # 格式正确，但域名可能不存在
]
# for email in test_emails:
#     try:
#         validate_email(email, check_deliverability=False)
#         print(f"✓ {email} - 格式合法")
#     except EmailNotValidError as e:
#         print(f"✗ {email} - {e}")


"""
4. phonenumbers —— 国际电话号码验证
使用场景：用户注册时验证手机号、国际化项目中处理多国电话格式、从文本中批量提取电话号码
"""

"""
5. python-stdnum —— 标准编号验证
"""
