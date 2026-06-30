import timeit
from datetime import datetime, timedelta, timezone

# 1. 获取当前日期和时间，分别使用 `datetime.now()` 和 `datetime.now(timezone.utc)` 输出，观察两者的区别
now = datetime.now()
utc_now = datetime.now(timezone.utc)
# print(f"Local now: {now}")
# print(f"UTC now: {utc_now}")
local_now = utc_now + timedelta(hours=8)
# print(f"Local now: {local_now}")


# 2. 使用 `strftime` 将当前时间格式化为 `"2026年06月30日 星期一 09:30:00"` 的格式
weeks = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
week_day = weeks[now.weekday()]
str_now_time = now.strftime("%Y{y}%m{m}%d{d} {w} %H:%M:%S").format(
    y="年", m="月", d="日", w=week_day
)
# print(str_now_time)


"""
3. 编写函数，接收一个 UTC 时间字符串（如 `"2026-06-30T01:30:00+00:00"`），
将其转换为北京时间并返回格式化字符串
"""


def utc_to_bz_time(utc_str: str) -> str:
    # 推荐使用 datetime.fromisoformat 直接解析 ISO 8601 格式的字符串
    utc_dt = datetime.fromisoformat(utc_str)
    tz_beijing = timezone(timedelta(hours=8))
    bj_dt = utc_dt.astimezone(tz_beijing)
    return bj_dt.strftime("%Y-%m-%d %H:%M:%S")


# print(utc_to_bz_time("2026-06-30T01:30:00+00:00"))


"""
4. 使用 `timeit` 比较以下三种字符串拼接方式的性能：

- `+` 运算符拼接
- `"".join()` 方法
- f-string 格式化
"""

# 为了避免 Python 编译器进行“常数折叠（Constant Folding）”优化（即在编译期就直接把 'hello' + 'world' 合并为 'helloworld'），
# 我们需要使用变量，并在 setup 中进行初始化。

number = 1000000

# 1. + 运算符拼接
t1 = timeit.timeit(stmt="a + b", setup="a = 'hello'; b = 'world'", number=number)

# 2. "".join() 方法
t2 = timeit.timeit(
    stmt="''.join([a, b])", setup="a = 'hello'; b = 'world'", number=number
)

# 3. f-string 格式化
t3 = timeit.timeit(stmt="f'{a}{b}'", setup="a = 'hello'; b = 'world'", number=number)

# print(f"+ 运算符拼接: {t1:.6f} 秒")
# print(f"join() 方法:   {t2:.6f} 秒")
# print(f"f-string 格式: {t3:.6f} 秒")


"""
5. 编写一个函数 `is_weekend(date_str)`，接收 `"YYYY-MM-DD"` 格式的字符串，判断该日期是否为周末
"""


def is_weekend(date_str: str) -> bool:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.weekday() >= 5


# print(is_weekend("2026-06-26"))


"""
6. 实现一个简单的 Token 管理器：生成带过期时间的 Token（UTC），提供验证函数判断是否过期，并支持续期操作
"""
import secrets  # noqa


class TokenManager:
    def __init__(self):
        # 存储结构为 {token: expire_time}
        self._tokens = {}

    def generate_token(self, expires_in: int = 3600) -> str:
        """生成一个带过期时间的 Token (UTC时间)"""
        token = secrets.token_hex(16)
        # 获取当前 UTC 时间并加上有效期
        expire_time = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        self._tokens[token] = expire_time
        return token

    def is_expired(self, token: str) -> bool:
        """验证 Token 是否已过期"""
        if token not in self._tokens:
            return True
        # 使用当前 UTC 时间与 Token 的过期时间进行比对
        return datetime.now(timezone.utc) > self._tokens[token]

    def renew_token(self, token: str, expires_in: int = 3600) -> bool:
        """对未过期的 Token 进行续期操作"""
        # 如果 Token 不存在，或者已经过期，则不允许续期
        if token not in self._tokens or self.is_expired(token):
            return False

        # 续期：从当前时间起重新计算过期时间
        self._tokens[token] = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        return True


# --- 验证测试 ---
if __name__ == "__main__":
    manager = TokenManager()

    # 1. 生成一个有效期 2 秒的 Token
    token = manager.generate_token(expires_in=2)
    print(f"生成 Token: {token}")
    print(f"初始检查是否过期: {manager.is_expired(token)}")  # 预期: False

    # 2. 模拟时间流逝（直接修改过期时间为过去，避免使用 time.sleep 阻塞）
    print("模拟时间过去 5 秒（手动修改过期时间为过去）...")
    manager._tokens[token] = datetime.now(timezone.utc) - timedelta(seconds=5)
    print(f"模拟后检查是否过期: {manager.is_expired(token)}")  # 预期: True

    # 3. 验证续期操作
    token2 = manager.generate_token(expires_in=10)
    print(f"\n生成新 Token2: {token2}")
    print(f"Token2 续期前是否过期: {manager.is_expired(token2)}")  # 预期: False

    success = manager.renew_token(token2, expires_in=60)
    print(f"Token2 续期结果: {success}")  # 预期: True

    # 尝试为过期的 Token 续期
    print(f"尝试为过期的旧 Token 续期: {manager.renew_token(token)}")  # 预期: False
