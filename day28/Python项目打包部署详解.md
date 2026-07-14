# Python 项目打包部署详解

> 写 Python
>
项目时，代码能在自己电脑上跑起来只是第一步。真正交付时，还要回答这些问题：别人怎么安装？依赖怎么固定？命令入口在哪里？配置和密钥怎么管理？如何部署到服务器、Docker、云平台或公司内网？本篇笔记围绕“从本地代码到可交付应用”的完整流程，讲清楚
> Python 项目打包和部署的常见做法。

---

## 一、先理解打包和部署分别解决什么问题

很多初学者会把“打包”和“部署”混在一起，其实它们关注的层次不同。

**打包**解决的是：如何把项目整理成一个标准产物，让别人可以安装、复用、发布。

常见产物包括：

- `wheel`：扩展名是 `.whl`，安装速度快，是现代 Python 包的主要分发格式。
- `sdist`：扩展名通常是 `.tar.gz`，表示源码包。
- 可执行命令：例如安装后可以直接运行 `my-tool`。
- Docker 镜像：把代码、依赖、运行环境一起封装。

**部署**解决的是：如何把项目放到目标环境中稳定运行。

目标环境可能是：

- 自己的另一台电脑。
- Linux 服务器。
- Docker 或 Docker Compose。
- Kubernetes。
- 云平台，例如 Render、Railway、Fly.io、AWS、Azure、阿里云、腾讯云。
- 公司内部服务器或 CI/CD 平台。

简单说：

```text
打包：把项目变成标准交付物。
部署：让交付物在目标环境长期运行。
```

---

## 二、不同类型 Python 项目的交付方式

Python 项目并不只有一种形态，不同项目适合不同打包部署方式。

### 2.1 脚本型项目

例如：

```text
batch_rename.py
clean_csv.py
download_images.py
```

这类项目可以很简单：

```bash
python clean_csv.py
```

如果要交给别人使用，至少应该提供：

- `README.md`：说明怎么安装、怎么运行。
- `requirements.txt`：说明依赖。
- 示例输入和输出。

适合学习和临时任务，但不适合长期维护的大项目。

### 2.2 命令行工具

例如：

```bash
my-tool init
my-tool run data.csv
my-tool export --format json
```

这类项目适合做成标准 Python 包，并配置命令入口。用户安装后可以直接运行命令：

```bash
pip install my-tool
my-tool --help
```

### 2.3 Web API 项目

例如 FastAPI、Flask、Django 项目。

本地运行可能是：

```bash
uvicorn app.main:app --reload
```

线上运行通常是：

```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker
```

这类项目部署时要考虑：

- 进程管理。
- 端口监听。
- 反向代理。
- 环境变量。
- 数据库连接。
- 日志收集。
- 健康检查。

### 2.4 后台任务项目

例如爬虫、定时任务、Celery worker、数据处理任务。

常见运行方式：

```bash
python -m app.tasks.sync_orders
celery -A app.worker worker -l info
```

这类项目部署时重点关注：

- 任务是否会重复执行。
- 失败后是否重试。
- 日志是否可追踪。
- 是否需要消息队列。
- 是否需要定时调度。

### 2.5 库项目

例如发布给别人 import 的工具库：

```python
from mylib import parse_file
```

这类项目更关注标准打包、版本号、API 稳定性和发布到 PyPI 或私有包仓库。

---

## 三、推荐的项目目录结构

现代 Python 项目推荐使用 `src` 布局：

```text
my_project/
├── README.md
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
├── .env.example
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── main.py
│       ├── cli.py
│       ├── config.py
│       └── services/
│           └── user_service.py
├── tests/
│   └── test_user_service.py
└── scripts/
    └── run_local.py
```

这些文件的职责：

- `README.md`：项目说明，包含安装、运行、测试、部署方式。
- `pyproject.toml`：项目元数据、构建系统、依赖、命令入口、工具配置。
- `requirements.txt`：简单项目的运行依赖，或部署时使用的锁定依赖。
- `requirements-dev.txt`：开发依赖，例如 `pytest`、`ruff`、`mypy`。
- `.env.example`：环境变量示例，不放真实密钥。
- `src/`：正式业务代码。
- `tests/`：自动化测试。
- `scripts/`：辅助脚本。

`src` 布局的好处是：测试时更接近真实安装后的使用方式，避免代码因为“当前目录刚好能 import”而掩盖打包问题。

---

## 四、虚拟环境和依赖管理

### 4.1 创建虚拟环境

每个项目都应该使用独立虚拟环境：

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux：

```bash
source .venv/bin/activate
```

安装依赖：

```bash
pip install requests fastapi uvicorn
```

导出依赖：

```bash
pip freeze > requirements.txt
```

别人复现环境：

```bash
pip install -r requirements.txt
```

### 4.2 requirements.txt 的优缺点

`requirements.txt` 简单直接，适合学习项目、小工具、部署脚本。

示例：

```text
fastapi==0.115.0
uvicorn==0.30.6
pydantic==2.8.2
```

优点：

- 容易理解。
- `pip install -r requirements.txt` 很通用。
- 服务器部署时很方便。

缺点：

- 不适合表达复杂项目元数据。
- 不方便配置命令入口。
- 不方便区分构建系统。

### 4.3 pyproject.toml 的作用

`pyproject.toml` 是现代 Python 项目的核心配置文件。它可以描述：

- 项目名称。
- 版本号。
- Python 版本要求。
- 运行依赖。
- 可选依赖。
- 构建后端。
- 命令行入口。
- 测试、格式化、类型检查工具配置。

一个最小示例：

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-project"
version = "0.1.0"
description = "A demo Python project"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.32.0",
]
```

如果项目使用 `src` 布局，可以加上：

```toml
[tool.setuptools.packages.find]
where = ["src"]
```

### 4.4 运行依赖和开发依赖分开

运行依赖是线上程序真正需要的包，例如：

- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `pydantic`
- `redis`

开发依赖是开发、测试、格式化需要的包，例如：

- `pytest`
- `ruff`
- `mypy`
- `black`
- `coverage`

在 `pyproject.toml` 中可以这样写：

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.5.0",
    "mypy>=1.10.0",
]
```

开发时安装：

```bash
pip install -e ".[dev]"
```

其中 `-e` 表示 editable install，也就是“可编辑安装”。你修改源码后，不需要重新安装包。

---

## 五、把项目打成标准 Python 包

### 5.1 安装构建工具

```bash
pip install build
```

### 5.2 执行构建

在项目根目录运行：

```bash
python -m build
```

构建后会生成：

```text
dist/
├── my_project-0.1.0-py3-none-any.whl
└── my_project-0.1.0.tar.gz
```

其中：

- `.whl` 是 wheel 包，推荐安装它。
- `.tar.gz` 是源码包，适合源码分发。

### 5.3 本地安装 wheel 包

```bash
pip install dist/my_project-0.1.0-py3-none-any.whl
```

安装后可以测试：

```bash
python -c "import my_project; print(my_project.__version__)"
```

如果这一步失败，说明项目打包配置或包结构有问题。

---

## 六、配置命令行入口

假设项目中有文件：

```text
src/my_project/cli.py
```

内容如下：

```python
def main() -> None:
    print("Hello from my-project")
```

可以在 `pyproject.toml` 中配置命令入口：

```toml
[project.scripts]
my-project = "my_project.cli:main"
```

安装项目：

```bash
pip install -e .
```

然后直接运行：

```bash
my-project
```

命令入口适合：

- 数据处理工具。
- 代码生成工具。
- 运维脚本。
- 爬虫工具。
- 项目初始化工具。

真实项目中通常会配合 `argparse`、`click` 或 `typer` 解析命令行参数。

---

## 七、发布到 PyPI 或私有包仓库

### 7.1 安装发布工具

```bash
pip install twine
```

### 7.2 检查构建产物

```bash
twine check dist/*
```

### 7.3 发布到 TestPyPI

TestPyPI 是测试用的 Python 包仓库，适合先演练发布流程。

```bash
twine upload --repository testpypi dist/*
```

### 7.4 发布到 PyPI

```bash
twine upload dist/*
```

发布前要确认：

- 包名没有被占用。
- 版本号没有重复。
- `README.md` 能正确渲染。
- 不包含密钥、内部地址、测试数据。
- 构建产物来自干净的代码状态。

### 7.5 版本号怎么定

常见版本号格式：

```text
主版本.次版本.补丁版本
```

例如：

```text
1.4.2
```

含义通常是：

- 主版本：不兼容的大改动。
- 次版本：向后兼容的新功能。
- 补丁版本：bug 修复。

例如：

```text
0.1.0  初始版本
0.2.0  增加新功能
0.2.1  修复 bug
1.0.0  第一个稳定版本
```

---

## 八、部署前要准备什么

无论部署到哪里，至少要准备这些内容：

### 8.1 README 中写清楚运行方式

示例：

```markdown
## 安装

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## 运行

uvicorn app.main:app --host 0.0.0.0 --port 8000

## 测试

pytest
```

### 8.2 环境变量示例

不要把真实密钥提交到 Git。

可以提供 `.env.example`：

```text
APP_ENV=dev
DATABASE_URL=postgresql://user:password@localhost:5432/app_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=change-me
```

真实部署环境中再配置真正的值。

### 8.3 健康检查接口

Web 项目建议提供：

```text
GET /health
```

返回：

```json
{
  "status": "ok"
}
```

健康检查可以被负载均衡、Docker、Kubernetes 或云平台用来判断应用是否正常。

### 8.4 日志输出到标准输出

线上部署时，日志一般应该输出到 stdout / stderr，而不是只写本地文件。

原因是：

- Docker 可以收集标准输出日志。
- 云平台可以自动采集日志。
- systemd 可以用 `journalctl` 查看日志。

---

## 九、部署方式一：直接部署到 Linux 服务器

这是最传统也最容易理解的方式。

### 9.1 服务器准备

安装 Python：

```bash
python3 --version
```

安装项目：

```bash
git clone https://example.com/my-project.git
cd my-project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

运行测试：

```bash
pytest
```

启动应用：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 9.2 使用 gunicorn 运行 FastAPI

开发环境常用：

```bash
uvicorn app.main:app --reload
```

生产环境更常见：

```bash
gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --workers 4
```

参数解释：

- `app.main:app`：`app/main.py` 里的 `app` 对象。
- `-k uvicorn.workers.UvicornWorker`：使用 uvicorn worker 处理 ASGI 应用。
- `--bind`：监听地址。
- `--workers`：工作进程数量。

### 9.3 使用 systemd 管理进程

直接在终端运行命令，一旦退出终端程序就会停止。生产环境通常用 systemd 管理进程。

示例 `/etc/systemd/system/my-project.service`：

```ini
[Unit]
Description = My Python Project
After = network.target

[Service]
User = www-data
WorkingDirectory = /opt/my-project
Environment = "APP_ENV=prod"
Environment = "DATABASE_URL=postgresql://user:password@localhost:5432/app_db"
ExecStart = /opt/my-project/.venv/bin/gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 --workers 4
Restart = always

[Install]
WantedBy = multi-user.target
```

启动：

```bash
sudo systemctl daemon-reload
sudo systemctl enable my-project
sudo systemctl start my-project
```

查看状态：

```bash
sudo systemctl status my-project
```

查看日志：

```bash
journalctl -u my-project -f
```

### 9.4 使用 Nginx 做反向代理

通常不会直接把 Python 服务暴露给公网，而是让 Nginx 接收公网请求，再转发给本机 Python 服务。

示例：

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

部署链路变成：

```text
用户浏览器
  -> Nginx:80/443
  -> gunicorn/uvicorn:8000
  -> Python 应用
```

---

## 十、部署方式二：Docker 部署

Docker 的核心价值是把运行环境也封装起来，减少“我这里能跑，你那里不能跑”的问题。

### 10.1 一个基础 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../note .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

构建镜像：

```bash
docker build -t my-project:0.1.0 .
```

运行容器：

```bash
docker run --rm -p 8000:8000 my-project:0.1.0
```

访问：

```text
http://localhost:8000
```

### 10.2 使用环境变量

```bash
docker run --rm \
  -p 8000:8000 \
  -e APP_ENV=prod \
  -e DATABASE_URL=postgresql://user:password@db:5432/app_db \
  my-project:0.1.0
```

不要把真实密钥写进 Dockerfile，因为镜像可能被推送、缓存或共享。

### 10.3 使用 .dockerignore

`.dockerignore` 可以减少构建上下文，避免把不必要文件复制进镜像。

示例：

```text
.git
.venv
__pycache__
.pytest_cache
.mypy_cache
.ruff_cache
dist
build
*.egg-info
.env
```

### 10.4 更适合 pyproject.toml 的 Dockerfile

如果项目使用 `pyproject.toml`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["my-project"]
```

这种方式表示：先把项目安装成一个标准包，再运行命令入口。

---

## 十一、部署方式三：Docker Compose

如果项目依赖数据库、Redis 等服务，Docker Compose 很方便。

示例 `docker-compose.yml`：

```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      APP_ENV: prod
      DATABASE_URL: postgresql://app_user:app_pass@db:5432/app_db
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: app_db
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: app_pass
    volumes:
      - pg_data:/var/lib/postgresql/data

  redis:
    image: redis:7

volumes:
  pg_data:
```

启动：

```bash
docker compose up -d
```

查看日志：

```bash
docker compose logs -f web
```

停止：

```bash
docker compose down
```

注意：`depends_on` 只表示启动顺序，不代表数据库已经完全可用。真实项目中，应用要能处理数据库暂时连接失败，或者在启动脚本中等待依赖服务就绪。

---

## 十二、部署方式四：云平台部署

很多云平台会自动识别 Python 项目。

常见要求包括：

- 有 `requirements.txt` 或 `pyproject.toml`。
- 指定 Python 版本。
- 指定启动命令。
- 配置环境变量。
- 暴露平台要求的端口。

例如 Web 项目的启动命令可能是：

```bash
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

注意 `$PORT` 通常由云平台注入，不能写死成 `8000`。

常见云部署检查项：

- 环境变量是否配置完整。
- 数据库连接地址是否正确。
- 应用是否监听 `0.0.0.0`。
- 端口是否使用平台提供的变量。
- 启动命令是否指向正确模块。
- 日志是否输出到标准输出。

---

## 十三、CI/CD：让打包部署自动化

手动部署容易出错。真实项目通常使用 CI/CD 自动完成检查、构建和部署。

一个常见流程：

```text
提交代码
  -> 运行测试
  -> 运行格式检查
  -> 构建 Python 包或 Docker 镜像
  -> 推送产物
  -> 部署到测试环境
  -> 部署到生产环境
```

### 13.1 GitHub Actions 示例

`.github/workflows/test.yml`：

```yaml
name: test

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Lint
        run: ruff check .

      - name: Test
        run: pytest
```

### 13.2 构建 Docker 镜像的流程

大致步骤：

```text
1. checkout 代码
2. 登录镜像仓库
3. docker build
4. docker push
5. 目标服务器拉取新镜像
6. 重启服务
```

镜像 tag 常见写法：

```text
my-project:latest
my-project:0.1.0
my-project:git-commit-sha
```

生产环境更推荐使用明确版本号或 commit sha，而不是只依赖 `latest`。

---

## 十四、配置、密钥和环境隔离

部署最容易出问题的地方之一就是配置。

### 14.1 不同环境使用不同配置

常见环境：

```text
local   本地开发
dev     开发环境
test    测试环境
staging 预发布环境
prod    生产环境
```

这些环境可能不同：

- 数据库地址。
- Redis 地址。
- 日志级别。
- 第三方 API 地址。
- 密钥。
- 调试模式。

### 14.2 密钥不要写进代码

不要这样：

```python
DATABASE_URL = "postgresql://user:real-password@prod-db:5432/app"
```

应该从环境变量读取：

```python
import os

DATABASE_URL = os.environ["DATABASE_URL"]
```

或者使用 `pydantic-settings` 做配置管理。

### 14.3 .env 文件只用于本地开发

本地可以使用 `.env`：

```text
DATABASE_URL=postgresql://user:password@localhost:5432/app_db
SECRET_KEY=dev-secret
```

但 `.env` 不应该提交到 Git。应该提交 `.env.example`，让别人知道需要哪些配置。

---

## 十五、部署前检查清单

部署前建议按这个清单检查：

- 项目可以在干净虚拟环境中安装。
- `pip install -r requirements.txt` 或 `pip install .` 能成功。
- 自动化测试通过。
- 入口命令清晰。
- README 有安装、运行、测试说明。
- 环境变量有 `.env.example`。
- 没有提交真实密钥。
- 日志输出到标准输出。
- Web 服务监听 `0.0.0.0`。
- 生产环境关闭 debug 模式。
- 数据库迁移脚本准备好。
- 依赖版本可复现。
- Docker 镜像可以构建并运行。
- 健康检查接口可用。
- 回滚方案明确。

---

## 十六、常见问题排查

### 16.1 本地能 import，安装后不能 import

常见原因：

- 包目录没有 `__init__.py`。
- `pyproject.toml` 没有正确配置 `src` 布局。
- 测试时依赖了当前目录，而不是安装后的包。

建议：

```bash
pip install -e .
pytest
```

用真实安装方式跑测试。

### 16.2 Docker 里找不到命令

可能原因：

- 依赖没有安装。
- 命令入口没有配置。
- `CMD` 写错。
- 工作目录不对。
- 镜像里没有复制对应文件。

排查：

```bash
docker run --rm -it my-project:0.1.0 sh
python --version
pip list
ls
```

### 16.3 线上端口访问不了

检查：

- 应用是否监听 `0.0.0.0`，而不是 `127.0.0.1`。
- 云平台是否要求使用 `$PORT`。
- 防火墙是否开放端口。
- Nginx 是否转发到正确端口。
- 容器是否映射端口。

### 16.4 线上数据库连接失败

检查：

- `DATABASE_URL` 是否正确。
- 数据库服务是否启动。
- 网络是否能访问。
- 用户名密码是否正确。
- 数据库是否允许远程连接。
- Docker Compose 中服务名是否写对，例如 `db` 而不是 `localhost`。

在 Docker Compose 里，应用连接数据库通常是：

```text
postgresql://app_user:app_pass@db:5432/app_db
```

不是：

```text
postgresql://app_user:app_pass@localhost:5432/app_db
```

因为 `localhost` 指的是当前容器自己。

### 16.5 修改代码后线上没变化

可能原因：

- 没有重新构建镜像。
- 服务器拉取的还是旧镜像。
- 服务没有重启。
- 浏览器或 CDN 缓存。
- 部署到了错误环境。

建议在启动日志中打印版本号或 commit sha，方便确认当前运行的是哪个版本。

---

## 十七、一个完整交付流程示例

假设有一个 FastAPI 项目，推荐流程可以是：

### 17.1 本地开发

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### 17.2 提交前检查

```bash
ruff check .
pytest
python -m build
```

### 17.3 构建 Docker 镜像

```bash
docker build -t my-api:0.1.0 .
```

### 17.4 本地验证镜像

```bash
docker run --rm -p 8000:8000 \
  -e APP_ENV=prod \
  -e DATABASE_URL=sqlite:///app.db \
  my-api:0.1.0
```

访问：

```text
http://localhost:8000/health
```

### 17.5 部署到服务器

```bash
docker pull registry.example.com/my-api:0.1.0
docker stop my-api || true
docker rm my-api || true
docker run -d \
  --name my-api \
  --restart always \
  -p 8000:8000 \
  -e APP_ENV=prod \
  -e DATABASE_URL=postgresql://user:password@db:5432/app_db \
  registry.example.com/my-api:0.1.0
```

### 17.6 查看运行状态

```bash
docker ps
docker logs -f my-api
```

---

## 十八、学习阶段推荐路线

如果是从零开始学习 Python 项目交付，可以按这个顺序：

1. 先掌握 `venv`、`pip`、`requirements.txt`。
2. 再学习项目目录结构，尤其是 `src` 布局。
3. 学会写 `pyproject.toml`。
4. 学会 `pip install -e .` 和命令行入口。
5. 学会 `python -m build` 构建 wheel 和 sdist。
6. 学会用 Dockerfile 封装运行环境。
7. 学会用 Docker Compose 组合应用、数据库和 Redis。
8. 学会在服务器上用 systemd 或 Docker 长期运行服务。
9. 学会用 CI/CD 自动测试、构建和部署。
10. 最后再深入 Kubernetes、私有包仓库、灰度发布和监控告警。

不要一开始就追求复杂平台。先保证项目能被别人稳定安装、运行、测试，再逐步升级部署方式。

---

## 十九、总结

Python 项目的打包部署，本质上是在解决“代码如何可靠交付”的问题。

打包侧重点是：

- 项目结构是否规范。
- 依赖是否明确。
- 元数据是否完整。
- 是否能构建 wheel。
- 是否能安装后正常 import 和运行。

部署侧重点是：

- 目标环境是否可复现。
- 配置和密钥是否安全。
- 进程是否能长期运行。
- 日志是否能追踪。
- 服务是否能健康检查。
- 出问题时是否能排查和回滚。

学习时记住一条主线：

```text
本地能跑
  -> 别人能安装
  -> 测试能通过
  -> 产物能构建
  -> 环境能复现
  -> 服务能长期运行
  -> 出问题能定位和回滚
```

当一个 Python 项目走完这条链路，它就不只是“代码”，而是一个真正可以交付、维护和部署的工程项目。
