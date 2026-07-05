# Python 网络编程、并发与测试实战

> 这份笔记面向已经掌握 Python 基础语法的学习者。目标不是记住某个库的所有参数，而是理解：Python 程序如何发起网络请求，什么时候选择 `requests` 或 `httpx`，并发到底解决什么问题，以及怎样用 `pytest` 给这些代码建立自动化测试。

---

## 一、为什么要学习网络编程、并发和测试

很多真实项目都绕不开这三件事：

- 从接口获取数据，例如调用天气 API、GitHub API、公司内部接口。
- 同时处理多个任务，例如批量下载网页、批量请求接口、并行处理文件。
- 保证代码稳定，例如改完代码后能快速知道有没有破坏旧功能。

如果把它们组合起来，一个常见任务可能是：

```text
读取一批用户名
↓
请求 GitHub API 获取用户信息
↓
并发加快请求速度
↓
把结果整理成列表或文件
↓
用 pytest 验证核心逻辑
```

学习顺序可以这样安排：

1. 先学同步网络请求：`requests`。
2. 再学更现代的 HTTP 客户端：`httpx`。
3. 然后理解并发：线程、进程、协程分别适合什么场景。
4. 最后用 `pytest` 测试纯逻辑、网络调用和异常分支。

---

## 二、网络编程基础

### 2.1 HTTP 请求是什么

HTTP 可以简单理解为客户端和服务器之间的一套交流规则。

当我们在浏览器输入一个网址时，大致发生了这些事：

1. 浏览器向服务器发送请求。
2. 服务器处理请求。
3. 服务器返回响应。
4. 浏览器把响应内容展示出来。

Python 程序也可以做同样的事。

例如请求一个接口：

```text
GET https://api.github.com/users/octocat
```

服务器可能返回 JSON：

```json
{
  "login": "octocat",
  "id": 583231,
  "html_url": "https://github.com/octocat"
}
```

常见 HTTP 方法包括：

- `GET`：获取资源。
- `POST`：提交数据，常用于创建资源或登录。
- `PUT`：整体更新资源。
- `PATCH`：局部更新资源。
- `DELETE`：删除资源。

常见状态码包括：

- `200`：成功。
- `201`：创建成功。
- `400`：请求参数错误。
- `401`：未登录或认证失败。
- `403`：没有权限，或者触发访问限制。
- `404`：资源不存在。
- `500`：服务器内部错误。

---

### 2.2 JSON 是接口中最常见的数据格式

很多接口返回的是 JSON。JSON 和 Python 数据结构很像：

```json
{
  "name": "Alice",
  "age": 18,
  "skills": ["Python", "SQL"]
}
```

在 Python 中通常会变成字典和列表：

```python
user = {
    "name": "Alice",
    "age": 18,
    "skills": ["Python", "SQL"],
}

print(user["name"])
print(user["skills"][0])
```

---

## 三、使用 requests 发送 HTTP 请求

### 3.1 安装 requests

`requests` 是 Python 生态中最常用的同步 HTTP 客户端之一。

安装：

```bash
pip install requests
```

---

### 3.2 发送 GET 请求

```python
import requests

url = "https://api.github.com/users/octocat"

response = requests.get(url, timeout=10)

print(response.status_code)
print(response.text)
```

这里有几个重点：

- `requests.get(...)` 发送 GET 请求。
- `timeout=10` 表示最多等待 10 秒。
- `response.status_code` 是 HTTP 状态码。
- `response.text` 是响应文本。

实际项目中，强烈建议写 `timeout`。如果不设置超时，网络异常时程序可能一直卡住。

---

### 3.3 解析 JSON 响应

```python
import requests

url = "https://api.github.com/users/octocat"

response = requests.get(url, timeout=10)
data = response.json()

print(data["login"])
print(data["html_url"])
```

`response.json()` 会把 JSON 字符串转换为 Python 对象，通常是字典或列表。

不过要注意：如果响应内容不是合法 JSON，`response.json()` 会抛出异常。

---

### 3.4 检查状态码

一个常见错误是：只要接口有返回，就直接读取数据。

不推荐：

```python
import requests

response = requests.get("https://api.github.com/users/not-exists-user", timeout=10)
data = response.json()

print(data["login"])
```

如果用户不存在，GitHub 会返回 `404`，响应里的 JSON 结构也不是正常用户信息。

更推荐：

```python
import requests

response = requests.get("https://api.github.com/users/not-exists-user", timeout=10)

if response.status_code == 404:
    print("用户不存在")
else:
    response.raise_for_status()
    data = response.json()
    print(data["login"])
```

`raise_for_status()` 会在状态码是 `4xx` 或 `5xx` 时抛出异常。

---

### 3.5 传递查询参数

接口常常需要查询参数，例如：

```text
https://api.example.com/search?q=python&page=1
```

用 `requests` 不需要自己拼接字符串，可以使用 `params`：

```python
import requests

url = "https://httpbin.org/get"

params = {
    "q": "python",
    "page": 1,
}

response = requests.get(url, params=params, timeout=10)
data = response.json()

print(data["args"])
print(response.url)
```

这样更清晰，也能避免 URL 编码问题。

---

### 3.6 发送 POST 请求

POST 常用于提交 JSON 数据：

```python
import requests

url = "https://httpbin.org/post"

payload = {
    "username": "alice",
    "password": "secret",
}

response = requests.post(url, json=payload, timeout=10)
response.raise_for_status()

data = response.json()
print(data["json"])
```

这里的 `json=payload` 会自动完成两件事：

1. 把 Python 字典转换成 JSON 字符串。
2. 设置合适的请求头 `Content-Type: application/json`。

---

### 3.7 设置请求头

很多接口需要请求头，例如 token、User-Agent、内容类型等。

```python
import requests

url = "https://api.github.com/user"

headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Accept": "application/vnd.github+json",
}

response = requests.get(url, headers=headers, timeout=10)
print(response.status_code)
```

注意：真实项目里不要把 token 直接写进代码。可以放到环境变量或配置文件中。

```python
import os

token = os.environ["GITHUB_TOKEN"]
```

---

### 3.8 使用 Session 复用连接和配置

如果要连续请求同一个网站，可以使用 `Session`：

```python
import requests

session = requests.Session()
session.headers.update({
    "User-Agent": "python-study-demo/1.0",
})

response = session.get("https://api.github.com/users/octocat", timeout=10)
response.raise_for_status()

data = response.json()
print(data["login"])
```

`Session` 的好处：

- 可以复用连接，减少重复建立连接的开销。
- 可以统一设置请求头、Cookie、认证信息。
- 适合封装成 API 客户端。

---

## 四、把 requests 封装成可复用函数

### 4.1 从脚本写法开始

一开始可能会这样写：

```python
import requests

response = requests.get("https://api.github.com/users/octocat", timeout=10)
data = response.json()

print(data["login"])
print(data["public_repos"])
```

这段代码能跑，但不好测试，也不好复用。

---

### 4.2 拆成函数

```python
from typing import Any

import requests


def fetch_github_user(username: str) -> dict[str, Any]:
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, timeout=10)

    if response.status_code == 404:
        raise ValueError(f"GitHub 用户不存在: {username}")

    response.raise_for_status()
    return response.json()


def format_user_summary(user: dict[str, Any]) -> str:
    return (
        f"{user['login']} | "
        f"followers={user['followers']} | "
        f"repos={user['public_repos']}"
    )


def main() -> None:
    user = fetch_github_user("octocat")
    summary = format_user_summary(user)
    print(summary)


if __name__ == "__main__":
    main()
```

这里把代码分成两类：

- `fetch_github_user`：负责网络请求。
- `format_user_summary`：负责纯数据处理。

后者不依赖网络，最容易测试。

---

## 五、使用 httpx

### 5.1 httpx 和 requests 有什么区别

`httpx` 是一个现代 HTTP 客户端，接口风格和 `requests` 比较接近，同时支持：

- 同步请求。
- 异步请求。
- 连接池。
- 超时配置。
- HTTP/2。

安装：

```bash
pip install httpx
```

如果只是写简单同步脚本，`requests` 已经很好用。

如果项目里已经使用 `asyncio`，或者需要异步并发请求，`httpx` 会更合适。

---

### 5.2 httpx 同步请求

```python
import httpx

url = "https://api.github.com/users/octocat"

response = httpx.get(url, timeout=10)
response.raise_for_status()

data = response.json()
print(data["login"])
```

可以看到，同步写法和 `requests` 很像。

---

### 5.3 使用 httpx.Client

类似 `requests.Session`，`httpx` 也有客户端对象：

```python
import httpx


def fetch_user(username: str) -> dict:
    with httpx.Client(
        base_url="https://api.github.com",
        headers={"User-Agent": "python-study-demo/1.0"},
        timeout=10,
    ) as client:
        response = client.get(f"/users/{username}")
        response.raise_for_status()
        return response.json()


user = fetch_user("octocat")
print(user["login"])
```

使用 `with` 的原因是：客户端内部持有连接池资源，用完后需要关闭。

---

### 5.4 httpx 异步请求

异步请求需要配合 `async`、`await` 和 `asyncio`。

```python
import asyncio

import httpx


async def fetch_user(username: str) -> dict:
    async with httpx.AsyncClient(
        base_url="https://api.github.com",
        timeout=10,
    ) as client:
        response = await client.get(f"/users/{username}")
        response.raise_for_status()
        return response.json()


async def main() -> None:
    user = await fetch_user("octocat")
    print(user["login"])


asyncio.run(main())
```

异步代码的核心规则：

- `async def` 定义异步函数。
- 调用异步函数会得到协程对象，不会立刻执行完。
- `await` 用来等待异步任务结果。
- `asyncio.run(...)` 用来启动异步程序入口。

---

## 六、并发基础

### 6.1 并发解决什么问题

假设要请求 5 个用户信息：

```text
octocat
torvalds
kennethreitz
pallets
psf
```

如果每个请求平均等待 1 秒，同步写法可能接近 5 秒。

但网络请求的大部分时间都在等待服务器响应。等待期间 CPU 很闲，所以可以让程序同时发起多个请求。

这就是并发的价值：在等待一个任务时，先去推进另一个任务。

---

### 6.2 并发和并行的区别

并发强调“任务在一段时间内交替推进”。

并行强调“多个任务在同一时刻真正同时运行”。

简单理解：

- 单核 CPU 上可以并发，但不能真正并行执行多个 Python 字节码。
- 多核 CPU 上可以并行，尤其适合多进程处理 CPU 密集任务。

---

### 6.3 I/O 密集和 CPU 密集

选择并发方式前，先判断任务类型。

I/O 密集任务：

- 网络请求。
- 读写文件。
- 数据库查询。
- 等待外部服务响应。

这类任务适合：

- 多线程。
- 异步协程。

CPU 密集任务：

- 图片处理。
- 视频转码。
- 大量数学计算。
- 大规模数据计算。

这类任务更适合：

- 多进程。
- C 扩展或 NumPy 这类释放 GIL 的库。
- 专门的计算框架。

---

## 七、使用线程并发

### 7.1 ThreadPoolExecutor 基本用法

对于同步函数，最容易上手的并发方式是线程池。

```python
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import requests


def fetch_github_user(username: str) -> dict[str, Any]:
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def main() -> None:
    usernames = ["octocat", "torvalds", "kennethreitz", "pallets", "psf"]

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_github_user, usernames)

    for user in results:
        print(user["login"], user["public_repos"])


if __name__ == "__main__":
    main()
```

`max_workers=5` 表示最多同时运行 5 个线程。

线程适合网络请求这类 I/O 密集任务，因为一个线程等待网络响应时，其他线程可以继续工作。

---

### 7.2 使用 as_completed 获取先完成的结果

`executor.map` 会按照输入顺序返回结果。如果想谁先完成就先处理谁，可以使用 `as_completed`：

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import requests


def fetch_github_user(username: str) -> dict[str, Any]:
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def main() -> None:
    usernames = ["octocat", "torvalds", "kennethreitz", "pallets", "psf"]

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fetch_github_user, username): username
            for username in usernames
        }

        for future in as_completed(futures):
            username = futures[future]
            try:
                user = future.result()
            except Exception as exc:
                print(f"{username} 请求失败: {exc}")
            else:
                print(user["login"], user["public_repos"])


if __name__ == "__main__":
    main()
```

这种写法更适合需要单独处理每个任务失败情况的场景。

---

### 7.3 线程并发的注意事项

线程不是越多越好。

如果线程太多，可能出现：

- 本机上下文切换开销变大。
- 目标服务器压力过大。
- 更容易触发接口限流。
- 日志和错误更难排查。

建议从较小的并发数开始，例如 `5`、`10`、`20`，根据接口限制和程序表现慢慢调整。

---

## 八、使用 asyncio 和 httpx 异步并发

### 8.1 asyncio.gather 基本用法

如果项目已经使用异步生态，可以用 `httpx.AsyncClient` 配合 `asyncio.gather`。

```python
import asyncio
from typing import Any

import httpx


async def fetch_github_user(
    client: httpx.AsyncClient,
    username: str,
) -> dict[str, Any]:
    response = await client.get(f"/users/{username}")
    response.raise_for_status()
    return response.json()


async def main() -> None:
    usernames = ["octocat", "torvalds", "kennethreitz", "pallets", "psf"]

    async with httpx.AsyncClient(
        base_url="https://api.github.com",
        timeout=10,
    ) as client:
        tasks = [
            fetch_github_user(client, username)
            for username in usernames
        ]
        users = await asyncio.gather(*tasks)

    for user in users:
        print(user["login"], user["public_repos"])


if __name__ == "__main__":
    asyncio.run(main())
```

这段代码会同时发起多个请求，并等待所有请求完成。

---

### 8.2 控制异步并发数量

直接 `gather` 很方便，但如果用户名很多，可能瞬间发起大量请求。

可以用 `asyncio.Semaphore` 控制并发数量：

```python
import asyncio
from typing import Any

import httpx


async def fetch_github_user(
    client: httpx.AsyncClient,
    username: str,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    async with semaphore:
        response = await client.get(f"/users/{username}")
        response.raise_for_status()
        return response.json()


async def main() -> None:
    usernames = ["octocat", "torvalds", "kennethreitz", "pallets", "psf"]
    semaphore = asyncio.Semaphore(3)

    async with httpx.AsyncClient(
        base_url="https://api.github.com",
        timeout=10,
    ) as client:
        tasks = [
            fetch_github_user(client, username, semaphore)
            for username in usernames
        ]
        users = await asyncio.gather(*tasks)

    for user in users:
        print(user["login"], user["public_repos"])


if __name__ == "__main__":
    asyncio.run(main())
```

`Semaphore(3)` 表示同一时间最多允许 3 个请求进入核心逻辑。

---

### 8.3 处理部分请求失败

默认情况下，`asyncio.gather` 中只要有一个任务抛异常，整体就会抛异常。

如果希望收集所有结果，可以设置 `return_exceptions=True`：

```python
import asyncio
from typing import Any

import httpx


async def fetch_github_user(
    client: httpx.AsyncClient,
    username: str,
) -> dict[str, Any]:
    response = await client.get(f"/users/{username}")
    response.raise_for_status()
    return response.json()


async def main() -> None:
    usernames = ["octocat", "not-exists-user-xyz", "psf"]

    async with httpx.AsyncClient(
        base_url="https://api.github.com",
        timeout=10,
    ) as client:
        tasks = [
            fetch_github_user(client, username)
            for username in usernames
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for username, result in zip(usernames, results):
        if isinstance(result, Exception):
            print(f"{username} 请求失败: {result}")
        else:
            print(result["login"])


if __name__ == "__main__":
    asyncio.run(main())
```

这种写法适合批量任务：一个失败不影响其他任务。

---

## 九、使用进程处理 CPU 密集任务

### 9.1 ProcessPoolExecutor 基本用法

如果任务是 CPU 密集型，多线程通常不一定能明显加速。

可以使用进程池：

```python
from concurrent.futures import ProcessPoolExecutor


def count_primes(limit: int) -> int:
    count = 0

    for number in range(2, limit):
        is_prime = True

        for factor in range(2, int(number ** 0.5) + 1):
            if number % factor == 0:
                is_prime = False
                break

        if is_prime:
            count += 1

    return count


def main() -> None:
    limits = [50_000, 60_000, 70_000, 80_000]

    with ProcessPoolExecutor() as executor:
        results = executor.map(count_primes, limits)

    for limit, result in zip(limits, results):
        print(limit, result)


if __name__ == "__main__":
    main()
```

多进程会启动多个 Python 进程，适合拆分较重的计算任务。

---

### 9.2 多进程的注意事项

多进程也有成本：

- 启动进程比启动线程更重。
- 进程之间传递数据需要序列化。
- 不适合大量很小的任务。
- Windows 下尤其要把入口放在 `if __name__ == "__main__":` 中。

所以选择并发模型时，可以先记住这个经验：

```text
网络请求、文件读写、数据库查询：优先线程或协程
大量 CPU 计算：考虑多进程
简单脚本：先写同步版本，再按瓶颈优化
```

---

## 十、pytest 基础

### 10.1 为什么需要测试

测试的价值不是证明代码永远没问题，而是让你修改代码时更有底气。

没有测试时，修改一个函数后可能要手动运行很多场景。

有测试时，可以用一个命令快速验证：

```bash
pytest
```

测试尤其适合覆盖：

- 数据转换逻辑。
- 参数校验逻辑。
- 异常分支。
- 边界情况。
- 不希望未来被改坏的业务规则。

---

### 10.2 安装 pytest

```bash
pip install pytest
```

常见目录结构：

```text
my_project/
├── src/
│   └── github_client/
│       ├── __init__.py
│       └── users.py
└── tests/
    └── test_users.py
```

---

### 10.3 写第一个测试

假设有一个函数：

```python
# src/calculator.py

def add(a: int, b: int) -> int:
    return a + b
```

测试文件：

```python
# tests/test_calculator.py

from calculator import add


def test_add_two_numbers() -> None:
    assert add(1, 2) == 3
```

运行：

```bash
pytest
```

pytest 会自动寻找：

- `test_*.py` 文件。
- `*_test.py` 文件。
- 名字以 `test_` 开头的函数。

---

### 10.4 测试纯函数最简单

前面写过一个格式化函数：

```python
from typing import Any


def format_user_summary(user: dict[str, Any]) -> str:
    return (
        f"{user['login']} | "
        f"followers={user['followers']} | "
        f"repos={user['public_repos']}"
    )
```

测试：

```python
from github_users import format_user_summary


def test_format_user_summary() -> None:
    user = {
        "login": "octocat",
        "followers": 100,
        "public_repos": 8,
    }

    result = format_user_summary(user)

    assert result == "octocat | followers=100 | repos=8"
```

这种测试不依赖网络、不依赖文件、不依赖数据库，所以速度快、结果稳定。

写代码时可以有意识地把“纯逻辑”从“外部调用”中拆出来。

---

### 10.5 测试异常

使用 `pytest.raises` 测试异常分支：

```python
import pytest


def parse_age(text: str) -> int:
    age = int(text)

    if age < 0:
        raise ValueError("年龄不能为负数")

    return age


def test_parse_age_rejects_negative_value() -> None:
    with pytest.raises(ValueError, match="年龄不能为负数"):
        parse_age("-1")
```

这里测试的是：传入负数时，函数应该抛出 `ValueError`。

---

### 10.6 参数化测试

如果同一个函数要测试多组输入，可以使用 `pytest.mark.parametrize`：

```python
import pytest


def normalize_username(username: str) -> str:
    return username.strip().lower()


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (" Alice ", "alice"),
        ("BOB", "bob"),
        ("  octocat", "octocat"),
    ],
)
def test_normalize_username(raw: str, expected: str) -> None:
    assert normalize_username(raw) == expected
```

这比写多个重复测试函数更简洁。

---

## 十一、pytest fixture

### 11.1 fixture 解决什么问题

测试中经常需要准备数据。

如果每个测试都写一遍，会重复：

```python
def test_a() -> None:
    user = {"login": "octocat", "followers": 100, "public_repos": 8}
    ...


def test_b() -> None:
    user = {"login": "octocat", "followers": 100, "public_repos": 8}
    ...
```

可以使用 fixture：

```python
import pytest


@pytest.fixture
def github_user() -> dict:
    return {
        "login": "octocat",
        "followers": 100,
        "public_repos": 8,
    }


def test_user_has_login(github_user: dict) -> None:
    assert github_user["login"] == "octocat"


def test_user_has_public_repos(github_user: dict) -> None:
    assert github_user["public_repos"] == 8
```

测试函数的参数名和 fixture 名字一致时，pytest 会自动注入。

---

### 11.2 使用 tmp_path 测试文件逻辑

pytest 内置 `tmp_path`，可以创建临时目录：

```python
from pathlib import Path


def save_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_save_text(tmp_path: Path) -> None:
    file_path = tmp_path / "hello.txt"

    save_text(file_path, "Hello")

    assert file_path.read_text(encoding="utf-8") == "Hello"
```

这样不会污染项目目录，也不需要手动清理测试文件。

---

## 十二、测试网络请求代码

### 12.1 不要在单元测试中直接依赖真实网络

下面这种测试不太稳定：

```python
def test_fetch_github_user() -> None:
    user = fetch_github_user("octocat")
    assert user["login"] == "octocat"
```

它依赖很多外部条件：

- 当前网络是否正常。
- GitHub 是否可访问。
- 接口是否限流。
- 返回字段是否变化。
- 测试运行环境是否允许访问外网。

更推荐把网络层隔离出来，用假响应测试自己的逻辑。

---

### 12.2 用 monkeypatch 替换 requests.get

假设代码如下：

```python
# github_users.py

from typing import Any

import requests


def fetch_github_user(username: str) -> dict[str, Any]:
    response = requests.get(
        f"https://api.github.com/users/{username}",
        timeout=10,
    )

    if response.status_code == 404:
        raise ValueError(f"GitHub 用户不存在: {username}")

    response.raise_for_status()
    return response.json()
```

可以这样测试：

```python
# tests/test_github_users.py

from typing import Any

import pytest

from github_users import fetch_github_user


class FakeResponse:
    status_code = 200

    def json(self) -> dict[str, Any]:
        return {
            "login": "octocat",
            "followers": 100,
            "public_repos": 8,
        }

    def raise_for_status(self) -> None:
        pass


def test_fetch_github_user(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url: str, timeout: int) -> FakeResponse:
        assert url == "https://api.github.com/users/octocat"
        assert timeout == 10
        return FakeResponse()

    monkeypatch.setattr("github_users.requests.get", fake_get)

    user = fetch_github_user("octocat")

    assert user["login"] == "octocat"
```

`monkeypatch` 的作用是：测试期间临时替换某个对象，测试结束后自动恢复。

---

### 12.3 测试 404 分支

```python
from typing import Any

import pytest

from github_users import fetch_github_user


class NotFoundResponse:
    status_code = 404

    def json(self) -> dict[str, Any]:
        return {"message": "Not Found"}

    def raise_for_status(self) -> None:
        pass


def test_fetch_github_user_raises_when_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_get(url: str, timeout: int) -> NotFoundResponse:
        return NotFoundResponse()

    monkeypatch.setattr("github_users.requests.get", fake_get)

    with pytest.raises(ValueError, match="GitHub 用户不存在"):
        fetch_github_user("not-exists")
```

测试异常分支很重要。很多线上问题都不是“正常路径”出错，而是异常路径没有处理好。

---

### 12.4 更容易测试的写法：依赖注入

除了 monkeypatch，也可以把请求函数作为参数传入：

```python
from collections.abc import Callable
from typing import Any

import requests


ResponseGetter = Callable[..., Any]


def fetch_github_user(
    username: str,
    get: ResponseGetter = requests.get,
) -> dict[str, Any]:
    response = get(
        f"https://api.github.com/users/{username}",
        timeout=10,
    )

    if response.status_code == 404:
        raise ValueError(f"GitHub 用户不存在: {username}")

    response.raise_for_status()
    return response.json()
```

测试时直接传入假的 `get`：

```python
from typing import Any

from github_users import fetch_github_user


class FakeResponse:
    status_code = 200

    def json(self) -> dict[str, Any]:
        return {"login": "octocat"}

    def raise_for_status(self) -> None:
        pass


def test_fetch_github_user_with_injected_get() -> None:
    def fake_get(url: str, timeout: int) -> FakeResponse:
        return FakeResponse()

    user = fetch_github_user("octocat", get=fake_get)

    assert user["login"] == "octocat"
```

这种写法的好处是：函数依赖更明确，测试也不需要修改模块内部对象。

---

## 十三、测试 httpx 异步代码

### 13.1 安装 pytest-asyncio

测试异步函数通常需要插件：

```bash
pip install pytest-asyncio
```

异步测试示例：

```python
import pytest


async def async_add(a: int, b: int) -> int:
    return a + b


@pytest.mark.asyncio
async def test_async_add() -> None:
    result = await async_add(1, 2)

    assert result == 3
```

---

### 13.2 用 httpx.MockTransport 测试异步请求

`httpx` 提供了 `MockTransport`，可以不用真实网络就模拟响应。

业务代码：

```python
# async_github_users.py

from typing import Any

import httpx


async def fetch_github_user(
    client: httpx.AsyncClient,
    username: str,
) -> dict[str, Any]:
    response = await client.get(f"/users/{username}")

    if response.status_code == 404:
        raise ValueError(f"GitHub 用户不存在: {username}")

    response.raise_for_status()
    return response.json()
```

测试代码：

```python
# tests/test_async_github_users.py

import httpx
import pytest

from async_github_users import fetch_github_user


@pytest.mark.asyncio
async def test_fetch_github_user_with_mock_transport() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/users/octocat"
        return httpx.Response(
            200,
            json={
                "login": "octocat",
                "followers": 100,
                "public_repos": 8,
            },
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        base_url="https://api.github.com",
        transport=transport,
    ) as client:
        user = await fetch_github_user(client, "octocat")

    assert user["login"] == "octocat"
```

这种测试速度快、稳定，也不会消耗真实接口额度。

---

## 十四、一个完整小案例：批量获取 GitHub 用户信息

### 14.1 目标

我们写一个小模块，实现：

- 输入多个 GitHub 用户名。
- 并发请求用户信息。
- 输出简洁摘要。
- 对格式化逻辑和请求逻辑写测试。

---

### 14.2 项目结构

```text
github_demo/
├── requirements.txt
├── src/
│   └── github_demo/
│       ├── __init__.py
│       ├── client.py
│       └── cli.py
└── tests/
    ├── test_client.py
    └── test_cli.py
```

`requirements.txt`：

```text
httpx
pytest
pytest-asyncio
```

---

### 14.3 编写 client.py

```python
# src/github_demo/client.py

import asyncio
from typing import Any

import httpx


def format_user_summary(user: dict[str, Any]) -> str:
    return (
        f"{user['login']} | "
        f"name={user.get('name') or '-'} | "
        f"followers={user['followers']} | "
        f"repos={user['public_repos']}"
    )


async def fetch_user(
    client: httpx.AsyncClient,
    username: str,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    async with semaphore:
        response = await client.get(f"/users/{username}")

    if response.status_code == 404:
        raise ValueError(f"GitHub 用户不存在: {username}")

    response.raise_for_status()
    return response.json()


async def fetch_users(
    usernames: list[str],
    max_concurrency: int = 5,
) -> list[dict[str, Any]]:
    semaphore = asyncio.Semaphore(max_concurrency)

    async with httpx.AsyncClient(
        base_url="https://api.github.com",
        timeout=10,
        headers={"User-Agent": "python-study-demo/1.0"},
    ) as client:
        tasks = [
            fetch_user(client, username, semaphore)
            for username in usernames
        ]
        return await asyncio.gather(*tasks)
```

这里把核心逻辑分成三个函数：

- `format_user_summary`：格式化用户信息。
- `fetch_user`：请求单个用户。
- `fetch_users`：并发请求多个用户。

---

### 14.4 编写 cli.py

```python
# src/github_demo/cli.py

import argparse
import asyncio

from github_demo.client import fetch_users, format_user_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("usernames", nargs="+")
    parser.add_argument("--max-concurrency", type=int, default=5)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    users = asyncio.run(
        fetch_users(
            args.usernames,
            max_concurrency=args.max_concurrency,
        )
    )

    for user in users:
        print(format_user_summary(user))


if __name__ == "__main__":
    main()
```

运行：

```bash
python -m github_demo.cli octocat psf pallets --max-concurrency 3
```

---

### 14.5 测试格式化逻辑

```python
# tests/test_client.py

from github_demo.client import format_user_summary


def test_format_user_summary() -> None:
    user = {
        "login": "octocat",
        "name": "The Octocat",
        "followers": 100,
        "public_repos": 8,
    }

    result = format_user_summary(user)

    assert result == "octocat | name=The Octocat | followers=100 | repos=8"
```

---

### 14.6 测试异步请求逻辑

```python
# tests/test_client.py

import asyncio

import httpx
import pytest

from github_demo.client import fetch_user


@pytest.mark.asyncio
async def test_fetch_user() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/users/octocat"
        return httpx.Response(
            200,
            json={
                "login": "octocat",
                "name": "The Octocat",
                "followers": 100,
                "public_repos": 8,
            },
        )

    transport = httpx.MockTransport(handler)
    semaphore = asyncio.Semaphore(1)

    async with httpx.AsyncClient(
        base_url="https://api.github.com",
        transport=transport,
    ) as client:
        user = await fetch_user(client, "octocat", semaphore)

    assert user["login"] == "octocat"
```

---

### 14.7 测试 404 分支

```python
# tests/test_client.py

import asyncio

import httpx
import pytest

from github_demo.client import fetch_user


@pytest.mark.asyncio
async def test_fetch_user_raises_when_not_found() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"message": "Not Found"})

    transport = httpx.MockTransport(handler)
    semaphore = asyncio.Semaphore(1)

    async with httpx.AsyncClient(
        base_url="https://api.github.com",
        transport=transport,
    ) as client:
        with pytest.raises(ValueError, match="GitHub 用户不存在"):
            await fetch_user(client, "not-exists", semaphore)
```

---

## 十五、常见问题和反模式

### 15.1 不设置 timeout

不推荐：

```python
requests.get(url)
```

推荐：

```python
requests.get(url, timeout=10)
```

没有超时的网络请求可能无限等待。

---

### 15.2 把异常全部吞掉

不推荐：

```python
try:
    response = requests.get(url, timeout=10)
except Exception:
    pass
```

这会让失败静默发生，后续更难排查。

更推荐：

```python
import logging

logger = logging.getLogger(__name__)

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.RequestException:
    logger.exception("请求失败: %s", url)
    raise
```

---

### 15.3 在测试中调用真实外部接口

偶尔写集成测试可以，但普通单元测试不建议依赖真实网络。

更推荐：

- 纯逻辑直接测试。
- 网络请求用 mock、monkeypatch、MockTransport。
- 少量集成测试单独标记，必要时手动运行。

---

### 15.4 盲目提高并发数

并发数不是越大越好。

过高并发可能导致：

- 本机资源占用升高。
- 请求失败率增加。
- 被接口限流。
- 日志刷屏，问题更难定位。

推荐先从小并发开始，再根据实际结果调整。

---

### 15.5 在异步函数里调用阻塞函数

不推荐：

```python
import requests


async def fetch_data(url: str) -> dict:
    response = requests.get(url, timeout=10)
    return response.json()
```

`requests.get` 是阻塞调用，会卡住事件循环。

异步代码中更推荐：

```python
import httpx


async def fetch_data(client: httpx.AsyncClient, url: str) -> dict:
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
```

---

## 十六、学习路线建议

如果你想系统掌握这部分内容，可以按下面顺序练习：

1. 使用 `requests.get` 请求一个公开接口。
2. 学会读取状态码、响应头和 JSON 响应。
3. 学会处理 `404`、超时、连接失败等异常。
4. 把请求逻辑封装成函数，不要散落在脚本顶层。
5. 使用 `ThreadPoolExecutor` 批量请求多个接口。
6. 使用 `httpx.AsyncClient` 和 `asyncio.gather` 实现异步并发。
7. 使用 `Semaphore` 控制并发数量。
8. 学会用 `pytest` 测试纯函数。
9. 学会用 `pytest.raises`、`parametrize`、`fixture`。
10. 学会用 `monkeypatch` 或 `httpx.MockTransport` 测试网络代码。

不要一开始就追求复杂架构。先写出能跑的同步版本，再把可复用逻辑拆出来，最后根据性能瓶颈引入并发和测试。

---

## 总结

网络编程、并发和测试经常一起出现在真实项目里。

- `requests` 适合简单、同步的 HTTP 请求。
- `httpx` 既支持同步，也支持异步，适合现代项目。
- 线程适合 I/O 密集任务，例如网络请求和文件读写。
- 协程适合大量异步 I/O，尤其适合和 `httpx.AsyncClient` 搭配。
- 进程适合 CPU 密集任务，例如大量计算。
- `pytest` 可以让代码修改更有底气，尤其适合测试纯函数、异常分支和外部依赖的封装层。

真正实用的 Python 能力，不只是“会请求一个接口”，而是能把请求、并发、错误处理、测试组织成清晰可靠的代码。这样写出来的程序，不仅今天能跑，也更容易扩展、排查和交给别人维护。
