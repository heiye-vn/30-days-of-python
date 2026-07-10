"""
当内置的校验规则不够用时，可以使用装饰器自定义校验逻辑。

@field_validator: 用于校验单个字段
@model_validator：用于联合校验多个字段（比如：确认密码和密码是否一致）
"""

from datetime import date

from pydantic import BaseModel, ValidationError, field_validator, model_validator


class RegisterForm(BaseModel):
    username: str
    password: str
    confirm_password: str

    # 校验用户名不能包含空格
    @field_validator("username")
    @classmethod
    def username_must_not_contain_space(cls, v: str) -> str:
        if " " in v:
            raise ValueError("用户名不能包含空格")
        return v

    # 联合校验：确认密码是否一致
    @model_validator(mode="after")
    def check_password_match(self) -> "RegisterForm":
        if self.password != self.confirm_password:
            raise ValueError("两次输入的密码不一致")
        return self


"""
校验器的使用注意事项：不要在 field_validator 或 model_validator 中编写复杂的、有副作用的或依赖外部系统的业务逻辑

Pydantic 的核心定位是数据校验与解析，而不是业务逻辑执行
"""


# 数据清洗与标准化
class UserRegister(BaseModel):
    phone: str

    @field_validator("phone")
    @classmethod
    def format_phone(cls, v: str) -> str:
        # 去除空格、横线，统一格式化，这是纯粹的数据清洗
        cleaned = v.replace(" ", "").replace("-", "")
        if not cleaned.isdigit():
            raise ValueError("手机号必须全为数字")
        return cleaned


# 纯内存的数据关联校验
class FlightBooking(BaseModel):
    departure_date: date
    return_date: date

    @model_validator(mode="after")
    def check_dates(self) -> "FlightBooking":
        if self.return_date < self.departure_date:
            raise ValueError("返程时间不能早于出发时间")
        return self


if __name__ == "__main__":
    # --- 场景一：正常预定（返程时间晚于出发时间） ---
    print("--- 场景一：正常预定 ---")
    try:
        booking = FlightBooking(departure_date="2026-10-01", return_date="2026-10-07")
        print("预订成功！")
        print(
            f"出发日期：{booking.departure_date} （类型：{type(booking.departure_date)}）"
        )
        print(f"返程日期：{booking.return_date}（类型：{type(booking.return_date)}）")
    except ValidationError as e:
        print(f"预定失败：{e}")

    print("\n" + "=" * 40 + "\n")

    # --- 场景二：异常预定（返程时间早于出发时间，触发自定义校验）---
    print("--- 场景二：返程时间早于出发时间 ---")
    try:
        booking_fail = FlightBooking(
            departure_date="2026-10-07", return_date="2026-10-01"
        )
    except ValidationError as e:
        print("校验捕获成功！错误详情如下：")
        print(e.json(indent=2))

    print("\n" + "=" * 40 + "\n")

    # --- 场景三：传入了错误的日期格式（触发 Pydantic 内置的类型校验）---
    print("--- 场景三：传入错误的日期格式 ---")
    try:
        booking_invalid_type = FlightBooking(
            departure_date="invalid-date", return_date="2026-10-07"
        )
    except ValidationError as e:
        print("内置类型校验捕获成功！错误详情如下：")
        print(e.json(indent=2))
