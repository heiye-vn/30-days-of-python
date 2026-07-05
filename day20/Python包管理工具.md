# Python 包管理工具详解

> 本教程覆盖 Python 生态中所有主流包管理工具，从基础到进阶，帮你选对工具、用好工具。

---

## 目录

1. [为什么需要包管理工具](#一为什么需要包管理工具)
2. [pip：Python 包管理的基石](#二pippython-包管理的基石)
3. [虚拟环境：venv 与 virtualenv](#三虚拟环境venv-与-virtualenv)
4. [依赖文件：requirements.txt](#四依赖文件requirementstxt)
5. [pipx：全局 CLI 工具安装](#五pipx全局-cli-工具安装)
6. [Poetry：现代化依赖管理](#六poetry现代化依赖管理)
7. [uv：新一代极速包管理器（推荐）](#七uv新一代极速包管理器)
8. [Pipenv：pip 与虚拟环境合一](#八pipenvpip-与虚拟环境合一)
9. [Conda：数据科学与跨语言](#九conda数据科学与跨语言)
10. [工具对比与选型建议](#十工具对比与选型建议)
11. [实战：项目配置最佳实践](#十一实战项目配置最佳实践)

---

## 一、为什么需要包管理工具

Python 之所以强大，原因之一是海量的第三方库。截至 2024 年，PyPI 上的包数量已超过 50 万。你几乎可以用任何现成的库，但这也带来了管理上的难题：

```
requests 依赖 urllib3、certifi、charset-normalizer、idna
urllib3 又依赖自己的子依赖……
一层一层叠加，形成依赖树
```

包管理工具要解决的核心问题：

1. **安装与卸载** —— 把别人写的代码下载到本地环境
2. **版本控制** —— 同一包不同版本的冲突如何解决
3. **环境隔离** —— A 项目需要 `requests==2.28`，B 项目需要 `requests==2.31`，怎么共存
4. **可重复性** —— 同事/服务器/CI 能跑完全一样的环境

---

## 二、pip：Python 包管理的基石

`pip`（**P**ip **I**nstalls **P**ackages）是 Python 官方的包管理工具，Python 3.4+ 自带。

### 2.1 基础命令

```bash
# 安装包
pip install requests
pip install requests==2.31.0        # 指定版本
pip install "requests>=2.30,<3.0"   # 版本范围
pip install "requests[security]"    # 安装可选依赖

# 卸载
pip uninstall requests

# 升级
pip install --upgrade requests

# 查看已安装的包
pip list
pip show requests     # 查看某个包的详细信息

# 搜索（已禁用）
# pip search 已经不再支持，去 pypi.org 手动搜
```

### 2.2 国内镜像源加速

PyPI 服务器在国外，国内下载经常很慢。配置镜像源可以大幅提升速度：

```bash
# 临时使用镜像
pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple

# 永久配置（写入全局配置文件）
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
```

常用镜像源：

| 提供商 | 地址 |
|--------|------|
| 清华大学 | `https://pypi.tuna.tsinghua.edu.cn/simple` |
| 阿里云 | `https://mirrors.aliyun.com/pypi/simple` |
| 腾讯云 | `https://mirrors.cloud.tencent.com/pypi/simple` |
| 豆瓣 | `https://pypi.doubanio.com/simple` |
| 中科大 | `https://pypi.mirrors.ustc.edu.cn/simple` |

### 2.3 pip install 的流程

```
pip install requests==2.31.0
    │
    ├─ 1. 解析依赖约束
    ├─ 2. 从 PyPI 查找候选版本
    ├─ 3. 下载 wheel 文件（.whl）
    ├─ 4. 解析依赖树（certifi, urllib3, idna...）
    │   └─ 递归解析所有依赖的依赖
    ├─ 5. 下载所有依赖包
    └─ 6. 安装到 site-packages 目录
```

### 2.4 pip 的常见问题

- **依赖解析慢** —— 特别是复杂冲突时，可能要等很久
- **没有环境隔离** —— 全局安装会污染系统 Python
- **需要配 venv 使用** —— 单独使用不够方便
- **没有锁文件（lock 文件）** —— 无法精确保存和复现环境

这些问题就是后续工具出现的原因。

---

## 三、虚拟环境：venv 与 virtualenv

### 3.1 为什么需要虚拟环境？

```bash
# 项目A 依赖 requests==2.28.0
# 项目B 依赖 requests==2.31.0
# 两个项目共用一个环境 → 冲突！

# 解决方案：每个项目一个独立的虚拟环境
```

虚拟环境为每个项目创建一个隔离的 Python 环境，各项目的依赖互不干扰。

### 3.2 venv（Python 内置）

```bash
# 创建虚拟环境（在项目目录下生成 .venv 文件夹）
python -m venv .venv

# 激活虚拟环境
# Linux / macOS:
source .venv/bin/activate
# Windows (CMD):
.venv\Scripts\activate.bat
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 激活后，终端提示符前会显示 (.venv)
(.venv) C:\my-project> pip install requests

# 退出虚拟环境
deactivate
```

### 3.3 virtualenv（第三方，更快）

```bash
pip install virtualenv

# 创建虚拟环境
virtualenv .venv

# 指定 Python 版本
virtualenv --python=python3.12 .venv

# 激活方式与 venv 相同
```

### 3.4 .gitignore 配置

创建虚拟环境后，一定要在 `.gitignore` 里加上：

```gitignore
.venv/
__pycache__/
*.pyc
```

---

## 四、依赖文件：requirements.txt

### 4.1 基本使用

```bash
# 导出当前环境所有已安装的包
pip freeze > requirements.txt

# requirements.txt 内容示例：
certifi==2024.2.2
charset-normalizer==3.3.2
idna==3.6
requests==2.31.0
urllib3==2.2.1

# 根据文件安装依赖
pip install -r requirements.txt
```

### 4.2 requirements.txt 的问题

- `pip freeze` 会导出当前环境所有包（包括传递依赖），**不是**你手动安装的
- 没有区分直接依赖和传递依赖：

  ```txt
  # requirements.txt 里看不出来
  requests==2.31.0  # 直接依赖
  urllib3==2.2.1    # 这是 requests 的依赖
  ```

- **不能**区分开发依赖和生产依赖

### 4.3 pip-tools：更优的依赖管理

```bash
# 安装 pip-tools
pip install pip-tools

# requirements.in 里只写你真正需要的包
requests
fastapi
uvicorn

# 编译生成 requirements.txt（含所有依赖的精确版本）
pip-compile requirements.in > requirements.txt

# 安装（pip-sync 只安装需要的包）
pip-sync requirements.txt
```

**pip-tools 的工作流：**
- `requirements.in` —— 只写直接依赖
- `pip-compile` —— 自动生成完整的依赖清单（含所有子依赖）
- `pip-sync` —— 精确同步环境（只安装需要的，删除多余的）

---

## 五、pipx：全局 CLI 工具安装

### 5.1 pipx 解决什么问题

你想全局使用一些 Python CLI 工具（如 `black`、`ruff`、`poetry`），但又不想污染系统环境：

```bash
# 问题：pip 全局安装 black
pip install black  # 安装到系统 Python
# 但可能与其他包冲突

# 解决方案：pipx 为每个 CLI 工具创建独立环境
pipx install black  # 独立隔离，不影响项目
```

### 5.2 使用方式

```bash
# 安装 pipx
pip install pipx
pipx ensurepath  # 确保 pipx 工具在 PATH 中

# 安装 CLI 工具
pipx install black
pipx install ruff
pipx install poetry
pipx install httpie

# 查看已安装的工具
pipx list

# 直接使用（每个工具有自己的隔离环境）
black .
ruff check .

# 升级
pipx upgrade black

# 卸载
pipx uninstall black
```

### 5.3 临时运行（不安装）

```bash
# 临时下载并运行，用完即销毁
pipx run black --check .
pipx run ruff check .

# 类似 npx（Node.js 的临时运行工具）
```

---

## 六、Poetry：现代化依赖管理

Poetry 是目前最流行的现代 Python 包管理工具之一（2018 年发布），它将**项目创建、依赖管理、打包发布**融为一体，提供了一站式体验。

### 6.1 安装

```bash
# 推荐用 pipx 安装（隔离环境）
pipx install poetry

# 验证安装
poetry --version
```

### 6.2 创建项目

```bash
# 创建新项目
poetry new my-project
# 生成的目录结构：
# my-project/
# ├── pyproject.toml    # 项目配置（类似 package.json）
# ├── README.md
# ├── my_project/
# │   └── __init__.py
# └── tests/
#     └── __init__.py

# 在已有项目中初始化
cd existing-project
poetry init  # 交互式创建 pyproject.toml
```

### 6.3 pyproject.toml 文件

```toml
[tool.poetry]
name = "my-project"
version = "0.1.0"
description = "My awesome project"
authors = ["Your Name <your@email.com>"]

[tool.poetry.dependencies]
python = "^3.11"
requests = "^2.31.0"
fastapi = "^0.110"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
ruff = "^0.3"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### 6.4 依赖管理

```bash
# 添加依赖
poetry add requests
poetry add requests==2.31.0
poetry add "fastapi[all]"

# 添加开发依赖（如 pytest、代码工具）
poetry add --group dev pytest mypy

# 移除依赖
poetry remove requests

# 安装所有依赖
poetry install

# 在虚拟环境中运行命令
poetry run python main.py
poetry run pytest

# 更新依赖
poetry update
poetry update requests  # 只更新指定包
```

### 6.5 poetry.lock 文件

```bash
# 首次 poetry install 会生成 poetry.lock
# 它锁定了所有依赖的精确版本（包括传递依赖）

# 团队成员只需：
poetry install
# 就能安装完全一致的环境

# poetry.lock 应提交到 Git
```

### 6.6 虚拟环境管理

```bash
# 列出所有虚拟环境
poetry env list

# 使用指定 Python 版本
poetry env use python3.12

# 进入 Poetry 的虚拟环境 shell
poetry shell

# 获取环境路径
poetry env info --path
```

### 6.7 Poetry 的优点与缺点

**优点：**
- 统一的 `pyproject.toml` 替代 `setup.py` + `requirements.txt`
- 内置 lock 文件（精确复现环境）
- 自动管理虚拟环境，无需手动 venv
- 支持发布到 PyPI

**缺点：**
- 依赖解析较慢（复杂项目可能要等很久）
- 安装 Poetry 本身需要额外步骤
- 速度比 uv 慢不少

---

## 七、uv：新一代极速包管理器

**uv 是 Astral（开发 ruff 的公司）2024 年推出的 Rust 编写的 Python 包管理器，速度比 pip 快 10-100 倍。**

### 7.1 安装

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或通过 pip
pip install uv

# 验证
uv --version
```

### 7.2 作为 pip 的直接替代（drop-in replacement）

```bash
# 和 pip 一样使用
uv pip install requests
uv pip install requests==2.31.0
uv pip install fastapi uvicorn

# 卸载
uv pip uninstall requests

# 升级
uv pip install --upgrade requests

# 从 requirements.txt 安装
uv pip install -r requirements.txt

# 生成 requirements.txt
uv pip freeze > requirements.txt

# 查看已安装的包
uv pip list
```

### 7.3 Python 版本管理

```bash
# uv 可以自动下载和管理 Python 版本（无需 pyenv）
uv python install 3.12

# 查看可用版本
uv python list

# 查看当前项目使用的 Python
uv python find
```

### 7.4 创建项目（类似 pyproject.toml + .venv）

```bash
# 创建新项目
uv init my-project
cd my-project

# 添加依赖
uv add requests
uv add fastapi

# 添加开发依赖
uv add --dev pytest ruff

# 安装所有依赖
uv sync

# 在虚拟环境中运行
uv run python main.py

# uv run 自动激活环境，用完自动退出
```

### 7.5 uvx：临时运行 CLI 工具（替代 pipx）

```bash
# 临时运行，用完即销毁
uvx ruff check .
uvx black --check .

# 等同于
uv tool run black
```

### 7.6 uv tool：全局安装 CLI 工具（替代 pipx）

```bash
# 全局安装 CLI 工具
uv tool install black
uv tool install httpie

# 使用
black .

# 列出已安装的工具
uv tool list

# 升级
uv tool upgrade ruff

# 卸载
uv tool uninstall ruff
```

### 7.7 uv.lock 文件

```bash
# uv sync 会生成 uv.lock
# uv.lock 文件保存所有依赖的精确版本
# 只需 uv sync 即可恢复一致的环境
```

### 7.8 uv 的优势与不足

**优势：**
- **极速** —— Rust 编写，安装和解析比 pip 快 10-100 倍
- **统一管理** —— 一个工具替代 pip + venv + poetry + pipx + pyenv
- **兼容标准** —— 完全兼容 `requirements.txt` 和 `pyproject.toml`
- **Python 版本管理** —— 无需 pyenv
- **跨平台** —— `uv.lock` 支持精确复现

**不足：**
- 2024 年初发布，生态还在成熟中
- 某些边缘情况可能遇到问题
- 复杂项目可能文档较少

---

## 八、Pipenv：pip 与虚拟环境合一

### 8.1 简介

Pipenv 是 2017 年推出的工具，目标是将 `pip` 和 `venv` 合并为一体。它使用 `Pipfile` 和 `Pipfile.lock`。

```bash
# 安装
pip install pipenv

# 初始化（进入项目目录）
cd my-project
pipenv install

# 添加依赖
pipenv install requests

# 添加开发依赖
pipenv install --dev pytest

# 进入虚拟环境
pipenv shell

# 在虚拟环境中运行命令
pipenv run python main.py

# 生成 lock 文件
pipenv lock

# 从 lock 文件安装
pipenv install --dev
```

### 8.2 Pipfile 示例

```toml
[[source]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
verify_ssl = true
name = "pypi"

[packages]
requests = "*"
fastapi = "*"
uvicorn = "*"

[dev-packages]
pytest = "*"
mypy = "*"

[requires]
python_version = "3.11"
```

### 8.3 Pipenv 的现状

**优点：**
- 环境与依赖一体化管理
- `Pipfile.lock` 锁定精确版本

**缺点：**
- 速度比 uv 慢很多，复杂项目可能要等很久
- 生态已逐渐被 uv 和 Poetry 取代
- 不再推荐用于新项目

---

## 九、Conda：数据科学与跨语言

### 9.1 Conda 简介

conda 是 Anaconda 公司推出的包管理器 + 环境管理工具，专为**数据科学和机器学习**设计。它不仅能安装 Python 包，还能安装非 Python 的依赖（如 CUDA、C 库等）。

安装方式：`miniconda`（轻量版）或 `anaconda`（完整版，内置 UI 和常用包）。

### 9.2 环境管理

```bash
# 创建环境
conda create -n myenv python=3.11

# 激活环境
conda activate myenv

# 退出环境
conda deactivate

# 列出所有环境
conda env list

# 删除环境
conda env remove -n myenv
```

### 9.3 包管理

```bash
# 从默认频道安装
conda install numpy pandas matplotlib

# 指定版本
conda install numpy=1.26

# 从 conda-forge 频道安装（更多包）
conda install -c conda-forge scikit-learn

# 更新
conda update numpy
conda update --all

# 导出/导入环境
conda env export > environment.yml
conda env create -f environment.yml
```

### 9.4 Conda 的独特优势

- **数据科学和机器学习**：numpy、pandas、torch 等复杂依赖的预编译二进制包
- **多语言支持**：能安装非 Python 的依赖（如 CUDA、R 语言）
- **跨平台**：Windows/macOS/Linux 一致体验
- **环境管理**：内置 Python 版本切换

**缺点：**
- 包体积较大（Anaconda 完整版 1-10 GB）
- 与 PyPI 上的新包有延迟（conda-forge 会快一些）
- 商业使用 Anaconda 需要付费（学术界免费）

---

## 十、工具对比与选型建议

### 10.1 功能对比表

| 工具 | 安装速度 | 依赖锁 | 虚拟环境 | Python 版本管理 | 适用场景 |
|------|----------|--------|----------|-----------------|----------|
| pip | 中 | ❌ | ❌（需 venv） | ❌ | 简单项目 |
| pip-tools | 中 | ✅ | ❌ | ❌ | 精细依赖控制 |
| Poetry | 中 | ✅ | ✅ | ❌ | 项目管理和发布 |
| uv | 极快 | ✅ | ✅ | ✅ | 新项目首选 |
| Pipenv | 慢 | ✅ | ✅ | ❌ | 已不推荐 |
| conda | 中 | ✅ | ✅ | ✅ | 数据科学/ML |

### 10.2 决策树

```
你的项目是什么类型？
│
├─ 数据科学/机器学习项目？
│   → conda / mamba
│
├─ 需要快速安装 + 管理 Python 版本？
│   → uv（uv python install 3.12）
│
├─ 需要完善的项目管理和发布？
│   → poetry（最成熟的方案）
│
├─ 只需要简单安装几个包？
│   → uv pip + uv tool（替代 pip + pipx）
│
└─ 最简单的基础方案？
    → pip + venv（足够用）
```

### 10.3 个人项目推荐

| 项目类型 | 推荐工具 |
|---------|----------|
| 学习 / 小脚本 | pip + venv |
| FastAPI Web 项目 | uv 或 Poetry |
| AI/ML 项目（torch 等） | conda + uv |
| CLI 工具发布 | Poetry 或 uv |
| 企业级项目 | uv（统一团队工具链） |

---

## 十一、实战：项目配置最佳实践

### 11.1 使用 uv 从零创建项目

```bash
# 1. 创建项目
uv init my-api
cd my-api

# 2. 添加生产依赖
uv add fastapi uvicorn

# 3. 添加开发依赖
uv add --dev pytest ruff mypy

# 4. 编写代码
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, World!"}

# 5. 运行
uv run uvicorn main:app --reload
```

### 11.2 使用 Poetry 完整配置

```bash
# 1. 创建项目
poetry new my-cli
cd my-cli

# 2. 配置 PyPI 镜像（国内加速）
poetry config repositories.tuna https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 添加依赖
poetry add click rich
poetry add --group dev pytest mypy black

# 4. 配置 CLI 入口（在 pyproject.toml 中）
# [tool.poetry.scripts]
# my-cli = "my_cli.main:cli"

# 5. 可编辑安装
poetry install

# 6. 直接使用
my-cli  # 即可调用
```

### 11.3 Git 提交规范

```gitignore
# 虚拟环境（不要提交）
.venv/
venv/

# Python 缓存
__pycache__/
*.pyc
*.pyo

# 提交依赖锁定文件
# uv 项目：uv.lock ✅
# Poetry 项目：poetry.lock ✅
# 传统项目：requirements.txt ✅

# 提交配置文件
pyproject.toml ✅
```

### 11.4 环境变量配置

```bash
# .env 文件（不要提交到 Git！）
DATABASE_URL=postgresql://localhost/mydb
SECRET_KEY=my-secret-key

# .gitignore 中添加
.env
```

### 11.5 Docker 中的包管理

```dockerfile
# Dockerfile 示例（使用 uv）
FROM python:3.12-slim

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 先复制依赖文件（利用 Docker 缓存层）
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 再复制代码
COPY . .

CMD ["uv", "run", "main.py"]
```

---

## 十二、常见问题 FAQ

**Q1: `pip install` 太慢怎么办？**
→ 用 uv（最快）或换国内镜像源

**Q2: 虚拟环境坏了怎么办？**
→ 删除 `.venv` 重新创建：`uv venv` 或 `python -m venv .venv`

**Q3: `pip freeze` 和 `requirements.txt` 的区别？**
→ `pip freeze` 是命令，`requirements.txt` 是文件。`pip freeze > requirements.txt` 导出当前所有包（包括传递依赖）。

**Q4: `uv.lock` 和 `poetry.lock` 的区别？**
→ 两者都是锁定依赖文件，格式不同，分别属于 uv 和 Poetry 生态。作用相同：精确保存和复现环境。

**Q5: 多个项目需要多个 Python 版本怎么办？**
→ uv 的 `uv python install 3.11 3.12` 或 pyenv。

**Q6: 如何从 `requirements.txt` 迁移到 uv/Poetry？**
→ uv：`uv init` 然后手动将依赖添加到 `pyproject.toml`。
→ Poetry：`poetry init`，然后用 `poetry add` 逐个添加。

---

## 总结

```
Python 包管理演进时间线：

pip (2008) → virtualenv (2009) → pipenv (2017) → poetry (2018) → uv (2024)
                                                              ↑
                                                            当前趋势

选对工具 = 少折腾，多写代码。
```

> **推荐：** 新项目首选 **uv**，它是 Python 包管理的未来。速度快、功能全、兼容标准，一个工具解决所有问题。
