# Python 包管理工具详解：pip、uv、Poetry、Conda 等

> 日期：2026-07-05  
> 适合阶段：已经会写基础 Python，希望开始规范管理第三方库、虚拟环境、项目依赖和发布包。

## 1. 为什么需要包管理工具

Python 生态里有大量第三方库，比如 `requests`、`numpy`、`pandas`、`fastapi`、`django`。包管理工具主要解决这些问题：

- **安装包**：从 PyPI 或私有仓库下载并安装第三方库。
- **管理版本**：指定 `requests==2.32.0`、`django>=5,<6` 这样的版本约束。
- **隔离环境**：不同项目可以使用不同版本的依赖，互不干扰。
- **记录依赖**：让别人或未来的自己能复现项目环境。
- **锁定依赖**：把直接依赖和间接依赖的精确版本固定下来，提升可复现性。
- **构建与发布**：把自己的代码打包成可安装的 Python 包，发布到 PyPI 或内部仓库。

简单说：包管理让 Python 项目从“我电脑上能跑”变成“任何人按说明都能跑”。

## 2. 先区分几个核心概念

### 2.1 包、模块、发行包

日常说“包”时容易混用几个概念：

- **模块 module**：一个 `.py` 文件，例如 `utils.py`。
- **导入包 import package**：包含 `__init__.py` 或命名空间包结构的目录，例如 `requests`。
- **发行包 distribution package**：发布到 PyPI 上的安装单位，例如 `pip install requests` 安装的 `requests`。

多数时候你只需要记住：`pip install xxx` 安装的是发行包，`import xxx` 导入的是模块或包。两者名字通常相同，但不总是相同，例如安装 `beautifulsoup4` 后通常 `from bs4 import BeautifulSoup`。

### 2.2 PyPI

PyPI，全称 Python Package Index，是 Python 第三方包的主要公共仓库。`pip` 默认会从 PyPI 查找和下载包，也可以配置公司内部私有源、镜像源或本地包源。

### 2.3 虚拟环境

虚拟环境是每个 Python 项目的独立依赖目录。它通常包含：

- 独立的 Python 解释器入口；
- 独立的 `site-packages`；
- 独立安装的第三方库。

推荐每个项目都使用虚拟环境，不要直接把项目依赖装进全局 Python。

常见创建方式：

```bash
python -m venv .venv
```

激活方式：

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

退出虚拟环境：

```bash
deactivate
```

### 2.4 `requirements.txt`

`requirements.txt` 是传统依赖清单，常见于 pip 工作流：

```txt
requests==2.32.3
fastapi>=0.115,<1
python-dotenv
```

安装：

```bash
python -m pip install -r requirements.txt
```

它的优点是简单通用；缺点是它本身不区分“直接依赖”和“间接依赖”，也不天然提供现代项目元数据。

### 2.5 `pyproject.toml`

`pyproject.toml` 是现代 Python 项目的核心配置文件。它可以记录：

- 项目名称、版本、描述；
- Python 版本要求；
- 运行依赖；
- 开发依赖；
- 构建后端；
- 格式化、类型检查、测试等工具配置。

示例：

```toml
[project]
name = "demo-project"
version = "0.1.0"
description = "A small Python demo"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.32",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "ruff>=0.6",
]
```

如果是新项目，建议优先理解并使用 `pyproject.toml`，而不是只依赖 `requirements.txt`。

## 3. pip：Python 默认包安装器

`pip` 是最基础、最通用的 Python 包安装工具。官方文档称它是 Python 的包安装器，可以从 PyPI 或其他索引安装包。

### 3.1 常用命令

查看版本：

```bash
python -m pip --version
```

升级 pip：

```bash
python -m pip install --upgrade pip
```

安装包：

```bash
python -m pip install requests
```

安装指定版本：

```bash
python -m pip install "requests==2.32.3"
```

安装版本范围：

```bash
python -m pip install "django>=5,<6"
```

卸载包：

```bash
python -m pip uninstall requests
```

查看已安装包：

```bash
python -m pip list
```

查看某个包信息：

```bash
python -m pip show requests
```

导出当前环境依赖：

```bash
python -m pip freeze > requirements.txt
```

从依赖文件安装：

```bash
python -m pip install -r requirements.txt
```

检查依赖冲突：

```bash
python -m pip check
```

### 3.2 为什么推荐 `python -m pip`

你会经常看到两种写法：

```bash
pip install requests
python -m pip install requests
```

更推荐第二种，因为它明确表示：使用当前这个 `python` 对应的 `pip`。这能减少多 Python 版本、多虚拟环境时“包装错地方”的问题。

### 3.3 pip 的适用场景

适合：

- 学习阶段安装第三方库；
- 简单脚本；
- 老项目；
- 需要最大兼容性的环境；
- Docker、CI 中安装 `requirements.txt`。

不太擅长：

- 自动维护项目元数据；
- 一体化管理虚拟环境、锁文件和 Python 版本；
- 区分应用依赖、开发依赖、可选依赖；
- 像现代项目管理器一样提供完整工作流。

### 3.4 pip 工作流示例

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install requests pytest
python -m pip freeze > requirements.txt
python -m pip install -r requirements.txt
```

这个工作流简单可靠。对于入门阶段，它仍然非常值得掌握。

## 4. uv：现代、高性能的一体化工具

`uv` 是 Astral 开发的 Python 包和项目管理工具，使用 Rust 编写。它的定位更接近“一把瑞士军刀”：可以替代或覆盖 `pip`、`pip-tools`、`pipx`、`poetry`、`pyenv`、`virtualenv`、`twine` 等工具的部分常见场景。

uv 的几个重点能力：

- 安装依赖速度很快；
- 管理虚拟环境；
- 管理项目依赖；
- 生成和同步锁文件；
- 运行单文件脚本并声明脚本依赖；
- 安装和切换 Python 版本；
- 运行命令行工具，类似 `pipx`；
- 提供兼容 pip 风格的 `uv pip` 接口。

### 4.1 安装 uv

Windows PowerShell：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS / Linux：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

也可以用 pip 安装：

```bash
python -m pip install uv
```

### 4.2 用 uv 管理项目

创建项目：

```bash
uv init my-project
cd my-project
```

添加依赖：

```bash
uv add requests
```

添加开发依赖：

```bash
uv add --dev pytest ruff
```

运行命令：

```bash
uv run python main.py
uv run pytest
```

同步环境：

```bash
uv sync
```

生成或更新锁文件：

```bash
uv lock
```

移除依赖：

```bash
uv remove requests
```

### 4.3 `uv run` 的意义

使用 `uv run` 时，uv 会确保命令在项目环境中执行。比如：

```bash
uv run python main.py
```

这通常比“先手动激活虚拟环境，再运行 Python”更稳定，也更适合写进 README、CI 或脚本里。

### 4.4 uv 的 pip 兼容接口

如果你已经熟悉 pip，可以从 `uv pip` 开始迁移：

```bash
uv venv
uv pip install requests
uv pip freeze
uv pip install -r requirements.txt
```

编译依赖文件：

```bash
uv pip compile requirements.in -o requirements.txt
```

同步环境到依赖文件：

```bash
uv pip sync requirements.txt
```

`sync` 和普通 `install` 的差别是：`sync` 会让环境尽量和锁定文件保持一致，多余的包可能被移除；`install` 更像是在现有环境上追加安装。

### 4.5 用 uv 管理 Python 版本

安装 Python：

```bash
uv python install 3.12
```

为当前项目固定 Python 版本：

```bash
uv python pin 3.12
```

用指定 Python 创建虚拟环境：

```bash
uv venv --python 3.12
```

### 4.6 uvx：运行一次性工具

`uvx` 是 `uv tool run` 的别名，类似 `npx` 或 `pipx run`。

例如临时运行 `ruff`：

```bash
uvx ruff check .
```

安装一个长期可用的命令行工具：

```bash
uv tool install ruff
```

### 4.7 uv 适用场景

适合：

- 新 Python 项目；
- 想要更快依赖安装速度；
- 想统一管理依赖、虚拟环境、锁文件和 Python 版本；
- 希望减少工具数量；
- 脚本、CLI、Web 项目、数据项目的日常开发。

需要注意：

- uv 比 pip 新，团队协作时要确认团队是否接受；
- 部分老项目或复杂发布流程仍可能沿用 pip、Poetry、Conda；
- 学习资料中 pip 仍然最多，所以 pip 基础不能跳过。

## 5. Poetry：依赖管理与打包发布工具

Poetry 是较成熟的 Python 依赖管理和打包工具。它强调：

- 在 `pyproject.toml` 中声明依赖；
- 自动解析依赖；
- 生成 `poetry.lock`；
- 管理虚拟环境；
- 构建和发布包。

### 5.1 常用命令

创建项目：

```bash
poetry new my-package
```

在已有目录初始化：

```bash
poetry init
```

添加依赖：

```bash
poetry add requests
```

添加开发依赖：

```bash
poetry add --group dev pytest ruff
```

安装依赖：

```bash
poetry install
```

运行命令：

```bash
poetry run python main.py
poetry run pytest
```

进入虚拟环境：

```bash
poetry shell
```

构建包：

```bash
poetry build
```

发布包：

```bash
poetry publish
```

### 5.2 Poetry 适用场景

适合：

- Python 库开发；
- 需要构建和发布到 PyPI；
- 团队已经采用 Poetry；
- 需要清晰的依赖分组和锁文件。

和 uv 的关系：

- Poetry 更早流行，生态和资料丰富；
- uv 速度更快，覆盖范围更广；
- 新项目可以优先考虑 uv，但维护 Poetry 项目时应尊重已有工作流。

## 6. Conda：环境和跨语言依赖管理

Conda 不只是 Python 包管理工具，它同时管理：

- Python 包；
- Python 版本；
- C/C++/Fortran 等二进制依赖；
- R 等其他语言包；
- 独立环境。

它在数据科学、机器学习、科学计算中很常见，因为这些领域经常依赖复杂的二进制库。

### 6.1 常用命令

创建环境：

```bash
conda create -n data-demo python=3.12
```

激活环境：

```bash
conda activate data-demo
```

安装包：

```bash
conda install numpy pandas
```

从 conda-forge 安装：

```bash
conda install -c conda-forge scipy
```

导出环境：

```bash
conda env export > environment.yml
```

从文件创建环境：

```bash
conda env create -f environment.yml
```

删除环境：

```bash
conda remove -n data-demo --all
```

### 6.2 Conda 和 pip 能不能混用

可以，但要谨慎。通常建议：

1. 先用 Conda 安装能从 Conda 仓库获得的核心二进制依赖；
2. 再用 pip 安装 Conda 没有的纯 Python 包；
3. 不要在同一个环境里频繁交叉升级同一个包。

对于普通 Web、脚本、CLI 项目，`venv + pip` 或 `uv` 通常更轻量。对于科学计算和 GPU 相关项目，Conda 仍然很有价值。

## 7. pipx：专门安装 Python 命令行工具

`pipx` 的定位很清楚：安装和运行 Python 写的命令行应用，并让每个应用处于独立虚拟环境中。

例如安装 `black`：

```bash
pipx install black
```

运行一次性工具：

```bash
pipx run cowsay hello
```

升级：

```bash
pipx upgrade black
```

卸载：

```bash
pipx uninstall black
```

适合用 pipx 安装的工具：

- `poetry`
- `black`
- `ruff`
- `httpie`
- `cookiecutter`

如果已经使用 uv，也可以用 `uv tool install` 和 `uvx` 覆盖许多 pipx 场景。

## 8. pip-tools：给 pip 增加锁定能力

`pip-tools` 常用于传统 pip 项目中，让依赖管理更可复现。

典型文件：

- `requirements.in`：手写的直接依赖；
- `requirements.txt`：编译后的完整依赖锁定结果。

示例：

```txt
# requirements.in
requests
fastapi
```

编译：

```bash
pip-compile requirements.in
```

安装并同步：

```bash
pip-sync requirements.txt
```

适合：

- 仍想使用 pip；
- 但又想要更稳定的锁定版本；
- 老项目不方便迁移到 Poetry 或 uv。

uv 的 `uv pip compile` 和 `uv pip sync` 也能覆盖类似场景。

## 9. build、setuptools、wheel、twine：打包发布相关工具

这些工具更偏“把自己的代码发布成包”。

### 9.1 setuptools

`setuptools` 是经典的 Python 打包构建工具。很多老项目使用 `setup.py`，现代项目更多把配置迁移到 `pyproject.toml`。

### 9.2 wheel

wheel 是 Python 的二进制分发格式，文件通常长这样：

```txt
demo_project-0.1.0-py3-none-any.whl
```

相比源码包，wheel 安装通常更快，也避免用户本地重复构建。

### 9.3 build

`build` 是 PyPA 推荐的构建前端之一，可根据 `pyproject.toml` 生成源码包和 wheel：

```bash
python -m pip install build
python -m build
```

生成结果通常在 `dist/` 目录下。

### 9.4 twine

`twine` 用来上传构建产物到 PyPI 或 TestPyPI：

```bash
python -m pip install twine
python -m twine upload dist/*
```

如果使用 uv，也可以查看 uv 的发布相关命令；如果使用 Poetry，也可以用 `poetry publish`。

## 10. 常见工具对比

| 工具 | 主要用途 | 是否管理虚拟环境 | 是否有锁文件 | 适合场景 |
| --- | --- | --- | --- | --- |
| `pip` | 安装 Python 包 | 否，需要配合 `venv` | 传统上常用 `requirements.txt`；新版 `pip lock` 仍需留意实验状态 | 入门、脚本、兼容老项目 |
| `venv` | 创建虚拟环境 | 是 | 否 | Python 标准库自带的环境隔离 |
| `uv` | 一体化包和项目管理 | 是 | 是，`uv.lock` | 新项目、快速安装、统一工作流 |
| `Poetry` | 依赖管理和打包发布 | 是 | 是，`poetry.lock` | 库开发、发布包、已有 Poetry 团队 |
| `Conda` | 环境和跨语言依赖管理 | 是 | 可用 `environment.yml` | 数据科学、机器学习、复杂二进制依赖 |
| `pipx` | 安装 Python CLI 工具 | 是，每个工具隔离 | 不强调 | 全局安装命令行工具 |
| `pip-tools` | 为 pip 生成锁定依赖 | 否 | 通过编译后的 requirements | 传统 pip 项目增强可复现性 |
| `setuptools` | 构建后端 | 否 | 否 | 打包构建 |
| `build` | 构建前端 | 否 | 否 | 生成 sdist 和 wheel |
| `twine` | 上传发布 | 否 | 否 | 发布到 PyPI / TestPyPI |

## 11. 如何选择

### 11.1 初学者

建议先掌握：

```bash
python -m venv .venv
python -m pip install requests
python -m pip freeze > requirements.txt
python -m pip install -r requirements.txt
```

理由：这是 Python 世界最通用的底层能力。看懂它后，学习 uv 或 Poetry 会容易很多。

### 11.2 新的普通 Python 项目

推荐优先考虑 uv：

```bash
uv init
uv add requests
uv run python main.py
```

理由：速度快，工作流完整，能少装很多工具。

### 11.3 已有老项目

先看项目已有文件：

- 有 `requirements.txt`：优先使用 pip 或 `uv pip`；
- 有 `poetry.lock`：优先使用 Poetry；
- 有 `uv.lock`：优先使用 uv；
- 有 `environment.yml`：优先使用 Conda；
- 有 `setup.py`：可能是老式打包项目，需要看 README。

不要在没有理解项目现有约定前随意替换工具。

### 11.4 数据科学或机器学习项目

如果涉及 `numpy`、`scipy`、`pytorch`、`tensorflow`、CUDA、GDAL 等复杂二进制依赖：

- Conda / Mamba 仍然很常见；
- uv 在很多纯 Python 或 wheel 完善的场景中很好用；
- 具体选择要看团队、平台和依赖来源。

### 11.5 Python 命令行工具

想全局安装某个命令，但不污染全局环境：

```bash
pipx install poetry
```

或者：

```bash
uv tool install ruff
```

## 12. 推荐学习路线

1. 学会 `venv + pip`：理解虚拟环境和安装位置。
2. 学会读 `requirements.txt`：知道版本固定和版本范围。
3. 学会读 `pyproject.toml`：理解现代项目元数据。
4. 学会 uv：用它创建项目、添加依赖、运行命令、同步环境。
5. 根据需要学习 Poetry：尤其是发布 Python 包时。
6. 根据方向学习 Conda：尤其是数据科学和机器学习。
7. 学会 pipx 或 `uv tool`：管理全局 CLI 工具。

## 13. 常见坑

### 13.1 包装到了错误的 Python 环境

现象：

```bash
pip install requests
python main.py
# ModuleNotFoundError: No module named 'requests'
```

原因通常是 `pip` 和 `python` 不是同一个环境。

解决：

```bash
python -m pip install requests
python -c "import requests; print(requests.__version__)"
```

### 13.2 忘记激活虚拟环境

检查当前 Python 路径：

```bash
python -c "import sys; print(sys.executable)"
```

如果路径不在当前项目的 `.venv` 下，说明可能没进项目环境。

使用 uv 时可以减少手动激活：

```bash
uv run python main.py
```

### 13.3 把虚拟环境提交到 Git

通常不应该提交 `.venv/`。在 `.gitignore` 中加入：

```gitignore
.venv/
__pycache__/
*.pyc
```

应该提交的是依赖声明文件，例如：

- `requirements.txt`
- `pyproject.toml`
- `uv.lock`
- `poetry.lock`
- `environment.yml`

### 13.4 只写宽松依赖，不锁版本

例如：

```txt
fastapi
requests
```

这在本地学习没问题，但在生产环境中可能因为上游包升级导致行为变化。更稳妥的方式是：

- 应用项目提交锁文件；
- CI 和部署使用锁文件安装；
- 定期主动升级依赖并测试。

### 13.5 混用太多工具

一个项目里同时出现 `requirements.txt`、`poetry.lock`、`uv.lock`、`environment.yml` 并不一定错，但要有明确规则。

建议在 README 中写清楚：

```md
本项目使用 uv 管理依赖：

uv sync
uv run pytest
```

## 14. 一套实用默认方案

如果没有历史包袱，可以这样做：

```bash
uv init my-project
cd my-project
uv add requests python-dotenv
uv add --dev pytest ruff
uv run python main.py
uv run pytest
```

项目里提交：

```txt
pyproject.toml
uv.lock
README.md
src/ 或项目代码
tests/
```

不提交：

```txt
.venv/
__pycache__/
.pytest_cache/
```

## 15. 小结

- `pip` 是基础，必须会。
- `venv` 负责隔离环境，和 pip 经常搭配使用。
- `uv` 是现代一体化工具，适合新项目，速度快，能力覆盖广。
- `Poetry` 适合依赖管理和打包发布，很多成熟项目仍在使用。
- `Conda` 适合科学计算、机器学习和复杂二进制依赖。
- `pipx` 或 `uv tool` 适合安装命令行工具。
- `pyproject.toml` 是现代 Python 项目的核心配置文件。
- 应用项目要重视锁文件和可复现安装。

## 16. 参考资料

- [pip 官方文档](https://pip.pypa.io/en/stable/)
- [uv 官方文档](https://docs.astral.sh/uv/)
- [Python Packaging User Guide：工具推荐](https://packaging.python.org/en/latest/guides/tool-recommendations/)
- [Poetry 官方文档](https://python-poetry.org/docs/)
- [Conda 官方文档](https://docs.conda.io/projects/conda/en/stable/)
- [pipx 官方文档](https://pipx.pypa.io/stable/)
- [pip-tools 官方文档](https://pip-tools.readthedocs.io/en/latest/)
- [setuptools 官方文档](https://setuptools.pypa.io/en/latest/)
