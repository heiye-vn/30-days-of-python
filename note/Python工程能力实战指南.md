# Python 工程能力实战指南

> 当代码从“能跑的小脚本”变成“需要长期维护的项目”时，真正拉开差距的往往不是某个语法点，而是工程能力：目录怎么组织、日志怎么记录、配置怎么管理、命令行怎么设计、依赖和测试怎么保证稳定。本篇笔记围绕实际项目场景，讲 Python 项目从脚本到工程化的常见做法。

---

## 一、什么是 Python 工程能力

很多初学者写 Python 的第一阶段是这样的：

```python
print("开始处理数据")

data = open("data.txt", encoding="utf-8").read()
result = data.upper()

print(result)
print("处理完成")
```

这段代码没有错，也能完成任务。但如果它变成真实项目，会很快遇到问题：

- 文件路径写死了，换一台机器就可能找不到文件。
- 处理过程只能靠 `print` 看，线上运行时很难追踪问题。
- 参数写在代码里，每次改输入输出都要改源码。
- 所有逻辑堆在一个文件里，测试、复用、排查都困难。
- 没有依赖说明，别人不知道该安装哪些包。

工程能力解决的就是这些问题。它让代码具备下面这些特征：

- **可读**：别人能快速理解项目结构和入口。
- **可维护**：新增功能时不用到处乱改。
- **可配置**：不同环境使用不同参数，不改源码。
- **可观测**：程序运行过程、错误原因、关键数据都能追踪。
- **可测试**：核心逻辑可以被自动验证。
- **可交付**：别人可以安装、运行、部署、复现结果。

简单说：语法让程序能运行，工程能力让程序能长期可靠地运行。

---

## 二、项目目录结构规范

### 2.1 小脚本可以简单，项目不能混乱

如果只是写一个临时脚本，下面这样完全可以：

```text
demo.py
data.csv
```

但一旦代码会继续迭代，就应该让目录表达职责。

一个常见的 Python 项目结构如下：

```text
my_project/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .gitignore
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── logging_config.py
│       ├── services/
│       │   └── user_service.py
│       └── utils/
│           └── file_utils.py
├── tests/
│   ├── test_config.py
│   └── test_user_service.py
├── configs/
│   ├── dev.toml
│   └── prod.toml
├── data/
│   ├── raw/
│   └── processed/
├── logs/
└── scripts/
    └── run_demo.py
```

这些目录的常见含义是：

- `README.md`：项目说明，告诉别人这是什么、怎么安装、怎么运行。
- `pyproject.toml`：现代 Python 项目的核心配置文件，可配置构建、格式化、测试、工具参数等。
- `requirements.txt`：依赖列表，适合简单项目或学习项目。
- `src/`：正式业务代码。
- `tests/`：测试代码。
- `configs/`：不同环境的配置文件。
- `data/`：数据文件，通常区分原始数据和处理后的数据。
- `logs/`：日志输出目录。
- `scripts/`：一次性脚本、辅助脚本、运维脚本。

### 2.2 为什么推荐 src 目录

很多项目也会这样写：

```text
my_project/
├── my_project/
│   ├── __init__.py
│   └── main.py
└── tests/
```

这也可以。但更推荐使用 `src/` 布局：

```text
my_project/
└── src/
    └── my_project/
        ├── __init__.py
        └── main.py
```

原因是：`src/` 布局可以减少“当前目录导入成功，但安装后导入失败”的问题。它会逼着你用更接近真实安装环境的方式运行和测试项目。

### 2.3 模块命名建议

Python 文件和包名建议使用小写加下划线：

```text
user_service.py
file_utils.py
data_loader.py
```

不推荐：

```text
UserService.py
file-utils.py
data loader.py
```

原因很简单：小写加下划线是 Python 社区最常见的风格，也更适合导入。

```python
from my_project.services.user_service import get_user
```

---

## 三、从脚本拆分成项目

### 3.1 一个不太工程化的脚本

假设你要读取一个文本文件，统计每个单词出现次数。

```python
# word_count.py

text = open("input.txt", encoding="utf-8").read()
words = text.lower().split()

counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1

for word, count in sorted(counts.items(), key=lambda item: item[1], reverse=True):
    print(word, count)
```

它的问题是：

- 输入文件写死为 `input.txt`。
- 统计逻辑和输出逻辑混在一起。
- 只能通过命令行看结果，不方便测试。
- 出错时没有清晰日志。

### 3.2 拆成可复用函数

第一步可以先拆函数：

```python
from pathlib import Path


def count_words(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts


def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def main() -> None:
    text = read_text("input.txt")
    counts = count_words(text)

    for word, count in sorted(counts.items(), key=lambda item: item[1], reverse=True):
        print(word, count)


if __name__ == "__main__":
    main()
```

现在 `count_words()` 就可以被单独测试：

```python
def test_count_words():
    assert count_words("hello hello python") == {"hello": 2, "python": 1}
```

这就是工程化的第一步：把“核心逻辑”从“运行入口”中分离出来。

---

## 四、logging 对比 print

### 4.1 print 适合什么场景

`print()` 不是不能用，它适合：

- 初学时观察变量。
- 临时脚本快速输出结果。
- 命令行工具向用户展示最终结果。
- Notebook 中做探索分析。

例如：

```python
name = "Alice"
print(name)
```

但在正式项目里，不建议用 `print()` 记录运行过程。

### 4.2 print 的局限

`print()` 有几个明显问题：

- 没有日志级别，无法区分调试信息、普通信息、警告、错误。
- 不方便统一输出到文件。
- 不方便控制格式，例如时间、模块名、行号。
- 不方便在不同环境中开关，例如开发环境打印详细日志，生产环境只记录重要日志。
- 多模块项目里，无法知道输出来自哪个模块。

### 4.3 logging 的基本用法

Python 标准库自带 `logging` 模块。

```python
import logging

logging.basicConfig(level=logging.INFO)

logging.debug("调试信息")
logging.info("程序开始运行")
logging.warning("配置项缺失，使用默认值")
logging.error("处理失败")
```

输出中会带上日志级别：

```text
INFO:root:程序开始运行
WARNING:root:配置项缺失，使用默认值
ERROR:root:处理失败
```

### 4.4 常见日志级别

从低到高，常见级别如下：

- `DEBUG`：调试信息，开发时使用。
- `INFO`：正常运行信息，例如任务开始、任务结束。
- `WARNING`：程序还能继续运行，但出现潜在问题。
- `ERROR`：某个操作失败，需要关注。
- `CRITICAL`：严重错误，程序可能无法继续运行。

实际项目中可以这样理解：

```python
logger.debug("当前请求参数: %s", params)
logger.info("用户登录成功: user_id=%s", user_id)
logger.warning("缓存未命中，准备查询数据库")
logger.error("调用支付接口失败", exc_info=True)
logger.critical("数据库连接不可用")
```

### 4.5 推荐写法：每个模块使用自己的 logger

不要在每个文件里都直接使用 `logging.info()`，更推荐这样：

```python
import logging

logger = logging.getLogger(__name__)


def process_file(path: str) -> None:
    logger.info("开始处理文件: %s", path)
    try:
        # 业务逻辑
        logger.info("文件处理完成: %s", path)
    except OSError:
        logger.exception("文件处理失败: %s", path)
        raise
```

`__name__` 会让日志知道自己来自哪个模块。例如 `my_project.services.file_service`。

### 4.6 为什么日志字符串推荐用占位符

推荐：

```python
logger.info("处理用户: %s", user_id)
```

不太推荐：

```python
logger.info(f"处理用户: {user_id}")
```

原因是：当日志级别被过滤掉时，占位符写法可以避免提前格式化字符串，尤其在日志很多或格式化成本较高时更合适。

### 4.7 同时输出到控制台和文件

一个简单的日志配置示例：

```python
import logging
from pathlib import Path


def setup_logging(log_file: str = "logs/app.log") -> None:
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )
```

使用：

```python
import logging

from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

logger.info("程序启动")
```

日志示例：

```text
2026-07-05 19:30:12,103 INFO [__main__] 程序启动
```

### 4.8 logging 和 print 的实际分工

如果你在写命令行工具，二者可以同时存在：

```python
logger.info("读取配置文件: %s", config_path)
print("任务执行成功，结果已保存到 output.csv")
```

经验规则：

- 给用户看的最终结果，用 `print()`。
- 给开发者和运维看的运行过程，用 `logging`。
- 错误堆栈、排查信息、关键状态，用 `logging`。

---

## 五、配置文件管理

### 5.1 为什么不要把配置写死在代码里

不推荐：

```python
DB_HOST = "localhost"
DB_PORT = 5432
DEBUG = True
DATA_PATH = "data/input.csv"
```

这样写的问题是：不同环境需要不同配置时，你只能改代码。

更好的做法是把配置从代码中抽离出来：

- 开发环境读取 `configs/dev.toml`
- 生产环境读取 `configs/prod.toml`
- 敏感信息从环境变量读取
- 命令行参数可以临时覆盖配置

### 5.2 常见配置来源

Python 项目常见配置来源有：

- `.env`：适合本地开发，保存环境变量。
- `.ini`：传统配置格式，标准库 `configparser` 支持。
- `.json`：通用格式，适合机器读写。
- `.yaml` / `.yml`：可读性强，但需要额外依赖 `PyYAML`。
- `.toml`：结构清晰，Python 3.11+ 标准库 `tomllib` 可读取。
- 环境变量：适合保存部署环境配置和敏感信息。
- 命令行参数：适合运行时临时指定参数。

### 5.3 使用 TOML 管理配置

例如 `configs/dev.toml`：

```toml
[app]
name = "word-counter"
debug = true

[paths]
input = "data/raw/input.txt"
output = "data/processed/result.txt"

[logging]
level = "INFO"
file = "logs/app.log"
```

Python 3.11+ 可以用标准库读取：

```python
import tomllib
from pathlib import Path


def load_config(path: str) -> dict:
    with Path(path).open("rb") as file:
        return tomllib.load(file)


config = load_config("configs/dev.toml")
print(config["paths"]["input"])
```

注意：`tomllib` 只能读取 TOML，不能写入 TOML。如果需要写入，通常使用第三方库。

### 5.4 使用 dataclass 表达配置结构

直接传 `dict` 虽然方便，但大型项目里容易出现拼错 key 的问题。

例如：

```python
input_path = config["path"]["input"]
```

这里如果写成 `path` 而不是 `paths`，运行时才会报错。

可以用 `dataclass` 把配置结构显式表达出来：

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class PathConfig:
    input: str
    output: str


@dataclass(frozen=True)
class LoggingConfig:
    level: str
    file: str


@dataclass(frozen=True)
class AppConfig:
    name: str
    debug: bool
    paths: PathConfig
    logging: LoggingConfig
```

加载配置：

```python
import tomllib
from pathlib import Path


def load_app_config(path: str) -> AppConfig:
    with Path(path).open("rb") as file:
        raw = tomllib.load(file)

    return AppConfig(
        name=raw["app"]["name"],
        debug=raw["app"]["debug"],
        paths=PathConfig(**raw["paths"]),
        logging=LoggingConfig(**raw["logging"]),
    )
```

这样后续使用会更清晰：

```python
config = load_app_config("configs/dev.toml")
print(config.paths.input)
```

### 5.5 环境变量适合放什么

环境变量常用于：

- 数据库密码
- API Key
- Token
- 当前运行环境，例如 `APP_ENV=prod`
- 部署平台注入的配置

读取环境变量：

```python
import os

api_key = os.getenv("API_KEY")
if not api_key:
    raise RuntimeError("缺少环境变量 API_KEY")
```

不要把密钥提交到 Git 仓库。可以提供 `.env.example` 说明需要哪些变量：

```text
API_KEY=your-api-key
DATABASE_URL=postgresql://user:password@localhost:5432/app
```

真正的 `.env` 应该加入 `.gitignore`。

### 5.6 配置优先级

实际项目经常会有多个配置来源。一个常见优先级是：

```text
命令行参数 > 环境变量 > 配置文件 > 代码默认值
```

例如：

- 默认输入文件是 `data/raw/input.txt`
- 配置文件里改成 `data/raw/dev.txt`
- 环境变量里指定 `INPUT_PATH=data/raw/prod.txt`
- 命令行运行时传入 `--input data/raw/test.txt`

最终应该使用命令行参数。

这种优先级的好处是：默认值保证程序能跑，配置文件适合长期配置，环境变量适合部署，命令行参数适合临时覆盖。

---

## 六、argparse 命令行程序

### 6.1 为什么需要命令行参数

如果程序这样写：

```python
input_path = "data/input.txt"
output_path = "data/output.txt"
```

每次换文件都要改代码。

命令行程序可以这样运行：

```bash
python -m word_counter --input data/raw/a.txt --output data/processed/a.txt
```

这就是 `argparse` 的价值：把“运行时变化的东西”变成命令行参数。

### 6.2 argparse 基本示例

```python
import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="统计文本文件中的单词频率")
    parser.add_argument("-i", "--input", required=True, help="输入文本文件路径")
    parser.add_argument("-o", "--output", default="result.txt", help="输出结果文件路径")
    parser.add_argument("--top", type=int, default=10, help="只输出前 N 个高频单词")
    parser.add_argument("--verbose", action="store_true", help="输出更详细的日志")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(args.input)
    print(args.output)
    print(args.top)
    print(args.verbose)


if __name__ == "__main__":
    main()
```

运行：

```bash
python word_counter.py --input input.txt --output result.txt --top 20 --verbose
```

### 6.3 常见参数类型

字符串参数：

```python
parser.add_argument("--name", type=str)
```

整数参数：

```python
parser.add_argument("--limit", type=int, default=100)
```

布尔开关：

```python
parser.add_argument("--debug", action="store_true")
```

限定可选值：

```python
parser.add_argument("--env", choices=["dev", "test", "prod"], default="dev")
```

多个值：

```python
parser.add_argument("--files", nargs="+")
```

### 6.4 子命令

复杂命令行工具通常会有子命令，例如：

```bash
python -m tool init
python -m tool run --config configs/dev.toml
python -m tool clean
```

`argparse` 支持子命令：

```python
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="初始化项目")
    init_parser.add_argument("--name", required=True)

    run_parser = subparsers.add_parser("run", help="运行任务")
    run_parser.add_argument("--config", default="configs/dev.toml")

    subparsers.add_parser("clean", help="清理输出文件")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init":
        print(f"初始化项目: {args.name}")
    elif args.command == "run":
        print(f"读取配置: {args.config}")
    elif args.command == "clean":
        print("清理完成")


if __name__ == "__main__":
    main()
```

### 6.5 命令行程序设计建议

命令行工具要注意使用体验：

- `--help` 信息要清楚。
- 必填参数不要太多。
- 常用参数提供短选项，例如 `-i`、`-o`。
- 危险操作提供确认或 `--dry-run`。
- 输出结果给用户看，运行过程写日志。
- 退出码要合理，成功为 `0`，失败为非 `0`。

---

## 七、综合示例：一个工程化的单词统计工具

下面用一个小项目串起来：目录结构、配置、日志、命令行参数。

### 7.1 目录结构

```text
word_counter/
├── README.md
├── pyproject.toml
├── configs/
│   └── dev.toml
├── data/
│   ├── raw/
│   │   └── input.txt
│   └── processed/
├── logs/
├── src/
│   └── word_counter/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── logging_config.py
│       └── counter.py
└── tests/
    └── test_counter.py
```

### 7.2 核心逻辑 counter.py

```python
from collections import Counter


def count_words(text: str) -> Counter[str]:
    words = text.lower().split()
    return Counter(words)


def format_top_words(counts: Counter[str], top: int) -> str:
    lines = []
    for word, count in counts.most_common(top):
        lines.append(f"{word}\t{count}")
    return "\n".join(lines)
```

这个文件不关心命令行、不关心配置、不关心日志文件路径。它只负责业务逻辑。

### 7.3 配置 config.py

```python
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    input_path: str
    output_path: str
    log_file: str
    log_level: str
    top: int


def load_config(path: str) -> AppConfig:
    with Path(path).open("rb") as file:
        raw = tomllib.load(file)

    return AppConfig(
        input_path=raw["paths"]["input"],
        output_path=raw["paths"]["output"],
        log_file=raw["logging"]["file"],
        log_level=raw["logging"]["level"],
        top=raw["app"].get("top", 10),
    )
```

### 7.4 日志 logging_config.py

```python
import logging
from pathlib import Path


def setup_logging(level: str, log_file: str) -> None:
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )
```

### 7.5 命令行入口 cli.py

```python
import argparse
import logging
from pathlib import Path

from word_counter.config import load_config
from word_counter.counter import count_words, format_top_words
from word_counter.logging_config import setup_logging

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="统计文本文件中的高频单词")
    parser.add_argument("--config", default="configs/dev.toml", help="配置文件路径")
    parser.add_argument("--input", help="覆盖配置文件中的输入路径")
    parser.add_argument("--output", help="覆盖配置文件中的输出路径")
    parser.add_argument("--top", type=int, help="输出前 N 个高频单词")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)

    input_path = args.input or config.input_path
    output_path = args.output or config.output_path
    top = args.top or config.top

    setup_logging(config.log_level, config.log_file)

    logger.info("读取输入文件: %s", input_path)
    text = Path(input_path).read_text(encoding="utf-8")

    logger.info("开始统计单词频率")
    counts = count_words(text)
    result = format_top_words(counts, top)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(result, encoding="utf-8")

    logger.info("结果已保存: %s", output_path)
    print(f"处理完成，结果已保存到 {output_path}")


if __name__ == "__main__":
    main()
```

### 7.6 配置文件 dev.toml

```toml
[app]
top = 10

[paths]
input = "data/raw/input.txt"
output = "data/processed/result.txt"

[logging]
level = "INFO"
file = "logs/app.log"
```

### 7.7 测试 test_counter.py

```python
from word_counter.counter import count_words, format_top_words


def test_count_words():
    counts = count_words("python python java")
    assert counts["python"] == 2
    assert counts["java"] == 1


def test_format_top_words():
    counts = count_words("a a b")
    assert format_top_words(counts, top=1) == "a\t2"
```

这个示例体现了几个原则：

- 核心逻辑独立，方便测试。
- 配置独立，方便切换环境。
- 日志独立，方便统一格式和输出位置。
- 命令行入口独立，方便用户运行。
- `print()` 只输出最终用户关心的信息。
- `logging` 记录程序内部运行过程。

---

## 八、依赖管理

### 8.1 requirements.txt

学习项目和简单项目中，最常见的是 `requirements.txt`：

```text
requests==2.32.3
pandas==2.2.2
pytest==8.2.2
```

安装：

```bash
pip install -r requirements.txt
```

建议固定版本，避免“昨天还能跑，今天安装新版本后不能跑”的问题。

### 8.2 pyproject.toml

现代 Python 项目越来越多使用 `pyproject.toml`。

一个简化示例：

```toml
[project]
name = "word-counter"
version = "0.1.0"
description = "A simple word counting CLI"
requires-python = ">=3.11"
dependencies = []

[project.scripts]
word-counter = "word_counter.cli:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

配置了 `[project.scripts]` 后，安装项目后可以直接运行：

```bash
word-counter --config configs/dev.toml
```

而不必每次写：

```bash
python -m word_counter.cli --config configs/dev.toml
```

### 8.3 虚拟环境

每个项目都应该使用独立虚拟环境。

创建：

```bash
python -m venv .venv
```

Windows 激活：

```bash
.venv\Scripts\activate
```

macOS / Linux 激活：

```bash
source .venv/bin/activate
```

为什么需要虚拟环境：

- 不污染系统 Python。
- 不同项目可以使用不同依赖版本。
- 更容易复现运行环境。

---

## 九、测试、格式化和静态检查

### 9.1 pytest

`pytest` 是 Python 最常用的测试框架之一。

安装：

```bash
pip install pytest
```

运行：

```bash
pytest
```

测试文件通常命名为：

```text
tests/test_xxx.py
```

测试函数通常命名为：

```python
def test_xxx():
    ...
```

### 9.2 什么代码最值得测试

优先测试：

- 数据转换逻辑。
- 金额、时间、权限等容易出错的逻辑。
- 配置解析逻辑。
- 边界条件。
- 曾经出过 bug 的地方。

不一定优先测试：

- 只有一两行的简单入口文件。
- 纯粹调用第三方库且没有业务判断的薄封装。
- 临时探索脚本。

### 9.3 格式化和检查

常见工具：

- `black`：自动格式化代码。
- `ruff`：快速检查代码风格和常见问题，也可以做格式化。
- `mypy`：静态类型检查。

例如使用 `ruff`：

```bash
ruff check .
ruff format .
```

类型标注不是为了让 Python 变成 Java，而是为了让复杂项目更容易理解：

```python
def read_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")
```

当函数越来越多时，类型标注可以显著降低理解成本。

---

## 十、路径处理：优先使用 pathlib

不推荐大量手写字符串拼接：

```python
path = "data/" + filename
```

推荐使用 `pathlib`：

```python
from pathlib import Path

data_dir = Path("data")
input_path = data_dir / "raw" / "input.txt"
text = input_path.read_text(encoding="utf-8")
```

创建目录：

```python
Path("data/processed").mkdir(parents=True, exist_ok=True)
```

写文件：

```python
Path("data/processed/result.txt").write_text("hello", encoding="utf-8")
```

`pathlib` 的好处是语义更清楚，也更适合跨平台。

---

## 十一、异常处理

### 11.1 不要裸 except

不推荐：

```python
try:
    run_task()
except:
    print("出错了")
```

这样会吞掉所有异常，包括 `KeyboardInterrupt`，也看不到真正原因。

推荐：

```python
import logging

logger = logging.getLogger(__name__)


try:
    run_task()
except FileNotFoundError:
    logger.exception("输入文件不存在")
    raise
except ValueError:
    logger.exception("数据格式不正确")
    raise
```

### 11.2 什么时候捕获异常

不要为了“看起来安全”到处捕获异常。通常只在这些地方捕获：

- 可以提供更清晰错误信息时。
- 可以进行重试、降级、清理资源时。
- 程序入口处需要统一记录错误时。

例如命令行入口可以这样：

```python
def main() -> int:
    try:
        run()
    except Exception:
        logger.exception("任务执行失败")
        return 1
    return 0
```

然后：

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

这样可以让命令行程序返回合理退出码。

---

## 十二、README 应该写什么

一个项目再好，如果别人不知道怎么运行，也很难使用。

`README.md` 至少应该包含：

- 项目简介：这个项目解决什么问题。
- 环境要求：Python 版本、系统要求。
- 安装方式：如何创建虚拟环境、安装依赖。
- 运行方式：常用命令示例。
- 配置说明：配置文件和环境变量怎么写。
- 测试方式：如何运行测试。
- 目录结构：重要目录分别做什么。

简单模板：

````markdown
# word-counter

统计文本文件中的高频单词。

## 安装

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 运行

```bash
python -m word_counter.cli --config configs/dev.toml
```

## 测试

```bash
pytest
```
````

---

## 十三、常见反模式

### 13.1 所有代码都写在 main.py

短期最快，长期最痛。

建议至少拆成：

- `cli.py`：命令行入口。
- `config.py`：配置读取。
- `logging_config.py`：日志配置。
- `service.py` 或具体业务模块：核心逻辑。

### 13.2 到处使用全局变量

不推荐：

```python
CONFIG = load_config()


def run():
    print(CONFIG["input"])
```

更推荐显式传参：

```python
def run(config: AppConfig) -> None:
    print(config.input_path)
```

显式传参更容易测试，也更容易理解依赖关系。

### 13.3 用 print 调试后忘记删除

临时调试可以用 `print()`，但提交前应该删除，或改成合适级别的日志。

```python
logger.debug("中间结果: %s", result)
```

### 13.4 捕获异常但什么也不做

不推荐：

```python
try:
    send_message()
except Exception:
    pass
```

这会让问题悄悄发生，后面更难排查。

至少应该记录日志：

```python
try:
    send_message()
except Exception:
    logger.exception("消息发送失败")
```

### 13.5 配置和密钥提交到仓库

不要提交：

```text
.env
secret.json
private_key.pem
```

可以提交：

```text
.env.example
configs/dev.example.toml
```

---

## 十四、一个实用的工程化检查清单

写完一个 Python 项目后，可以用下面的清单自查：

- 是否有清晰的 `README.md`？
- 是否说明了 Python 版本和依赖安装方式？
- 是否使用了虚拟环境？
- 是否把核心逻辑从入口文件中拆出来？
- 是否有必要的测试？
- 是否使用 `logging` 记录运行过程？
- 是否避免把密钥写进代码？
- 是否把可变参数放进配置文件、环境变量或命令行参数？
- 是否使用 `pathlib` 处理路径？
- 是否有 `.gitignore` 忽略 `.venv`、日志、缓存和密钥？
- 是否避免了裸 `except` 和无意义的 `pass`？
- 是否能在一台新机器上按文档复现运行？

---

## 十五、学习路线建议

如果你已经掌握 Python 基础语法，可以按下面顺序补工程能力：

1. 学会用函数拆分脚本。
2. 学会用 `pathlib` 处理文件路径。
3. 学会用 `logging` 替代项目中的调试 `print()`。
4. 学会用 `argparse` 编写命令行工具。
5. 学会用 TOML、JSON、环境变量管理配置。
6. 学会创建虚拟环境和维护依赖文件。
7. 学会用 `pytest` 写最小测试。
8. 学会整理 `README.md` 和项目目录结构。
9. 学会使用 `ruff`、`black` 等工具保持代码质量。
10. 最后再学习打包、发布、CI/CD、Docker 等更完整的交付能力。

工程化不是一上来就把项目做得很复杂，而是在项目复杂度上升之前，提前给代码留出清晰的组织方式。

---

## 总结

Python 工程能力的核心不是“显得专业”，而是解决真实问题：

- 项目目录结构让代码有秩序。
- `logging` 让程序运行过程可追踪。
- 配置文件和环境变量让程序适应不同环境。
- `argparse` 让脚本变成可复用的命令行工具。
- 虚拟环境和依赖文件让项目可以复现。
- 测试和静态检查让修改更有底气。

从学习角度看，可以先写出能跑的代码，再逐步把它整理成清晰、可靠、可维护的项目。真正的工程能力，就是让代码不仅今天能跑，明天、下个月、换个人接手时也能继续跑。
