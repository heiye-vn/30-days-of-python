# 30 Days of Python 学习项目 🐍

本项目用于记录在 30 天 Python 学习旅程中的代码练习与实战。

## 📁 目录结构

```text
.
├── .gitignore          # Git 忽略文件配置
├── README.md           # 项目自述文档
└── day01/              # python 相关命令练习
└── day02/              # 常用内置函数
└── day03/              # 运算符
└── day04/              # 字符串详解（特性、方法、格式化...）
└── day05/              # 列表（List）
└── day06/              # 元组（Tuple）
└── day07/              # 集合（Set）
└── day08/              # 字典（Dict）
└── day09/              # 条件语句
└── day10/              # 循环语句（Loop）
└── day11/              # 函数（Function）
└── day12/              # 模块（Module）
└── day13/              # 列表推导式
└── day14/              # 高阶函数、闭包、装饰器、生成器
└── day15/              # 常见类型错误
└── day16/              # 日期与时间处理
└── day17/              # 异常处理、打包、解包、展开
└── day18/              # 正则表达式
└── day19/              # 文件操作处理
└── day20/              # 包管理工具
└── day21/              # 面向对象编程（OPP）
└── day22/              # 上下文管理器、类型注解
└── day23/              # Pydantic 的使用
└── day24/              # logging 日志记录
└── day25/              # 迭代器、生成器、装饰器详解
└── day26/              # 异步编程详解
└── day27/              # 网络编程、并发处理，pytest 测试框架应用
└── day21/              # 面向对象编程（OPP）
```

---

## 🛠️ Python 环境管理与常用命令指南

在进行 Python 开发时，使用虚拟环境来隔离不同项目的依赖是一个非常好的工程习惯。

### 1. 虚拟环境管理 (venv)

#### 创建虚拟环境

在项目根目录下，使用 Python 自带的 `venv` 模块创建名为 `.venv` 的虚拟环境：

- **macOS / Linux**：
  ```bash
  python3 -m venv .venv
  ```
- **Windows**：
  ```cmd
  python -m venv .venv
  ```

#### 激活虚拟环境

使用虚拟环境前，需要先将其激活：

- **macOS / Linux**：
  ```bash
  source .venv/bin/activate
  ```
- **Windows (Command Prompt)**：
  ```cmd
  .venv\Scripts\activate.bat
  ```
- **Windows (PowerShell)**：
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

#### 查看当前环境

- windows cmd

```cmd
where python
```

- windows PowerShell

```powershell
Get-Command python | Select-Object -ExpandProperty Source
```

#### 查看当前环境安装的包

- **macOS / Linux**：
  ```bash
  pip list
  ```
- **Windows**：
  ```cmd
  pip list
  ```

#### 退出虚拟环境

当开发完毕，想要回到系统的全局 Python 环境时：

- **跨平台通用命令**：
  ```bash
  deactivate
  ```

---

### 2. 依赖管理 (pip)

在虚拟环境**激活状态**下，使用以下命令管理依赖：

- **安装依赖**：
  ```bash
  pip install <package_name>
  ```
- **保存当前环境依赖到文件**：
  ```bash
  pip freeze > requirements.txt
  ```
- **从文件批量安装依赖**：
  ```bash
  pip install -r requirements.txt
  ```
- **列出已安装的包**：
  ```bash
  pip list
  ```

---

### 3. Python 多版本管理与切换

当你的电脑上需要同时存在多个 Python 版本（例如 3.9、3.10、3.12 等），推荐使用以下工具进行版本管理与切换：

#### 方案 A：使用 `pyenv`（推荐，跨平台，Mac 极佳）

`pyenv` 可以让你轻松安装、卸载和切换全局或目录级别的 Python 版本。

- **安装指定版本**：
  ```bash
  pyenv install 3.12.0
  ```
- **查看已安装的所有版本**：
  ```bash
  pyenv versions
  ```
- **设置当前项目的 Python 版本**（会在当前目录下创建 `.python-version` 文件）：
  ```bash
  pyenv local 3.12.0
  ```
- **设置全局默认 Python 版本**：
  ```bash
  pyenv global 3.12.0
  ```

#### 方案 B：使用 Windows 自带的 `py` 启动器

Windows 安装 Python 时，通常会默认安装 Python Launcher (`py.exe`)，可以通过它指定版本运行：

- **查看已安装的版本列表**：
  ```cmd
  py --list
  ```
- **使用指定版本运行脚本**：
  ```cmd
  py -3.10 main.py
  py -3.12 main.py
  ```
- **使用指定版本创建虚拟环境**：
  ```cmd
  py -3.12 -m venv .venv
  ```

---

### Git 提交常用前缀分类大全

按改动类型划分前缀，覆盖开发全场景：

#### **1. 功能相关（核心业务改动）**

- `feat`：新增功能或页面（例如：`feat(用户模块): 新增手机号登录功能`）
- `fix`：修复普通 Bug 或问题（例如：`fix(订单页): 修复金额计算错误`）
- `modify`：修改已有功能（不新增、不修复Bug）
- `delete`：删除无用功能或文件
- `hotfix`：生产环境紧急修复（区别于普通的 fix）

#### **2. 优化与重构相关（不影响业务逻辑）**

- `refactor`：重构代码，不涉及功能新增或 Bug 修复（例如：`refactor: 用 map 代替 for 循环简化逻辑`）
- `perf`：优化代码或性能改进（例如：`perf: 减少数据库查询次数，降低响应时间`）

#### **3. 样式与文档相关**

- `style`：纯代码风格变动，不影响代码运行（如空格、缩进、ESLint修复等）
- `docs`：文档修改或注释变更（例如：`docs: 更新API使用文档和注释`）

#### **4. 构建、测试与工具相关**

- `test`：新增或修改测试用例
- `build`：构建工具或依赖相关的更改（如升级 Webpack）
- `ci`：持续集成配置相关的修改（如修改 GitHub Actions 构建流程）
- `chore`：对非 src 或 test 的项目配置修改（如更新项目依赖库版本）

#### **5. 其他特殊场景**

- `revert`：撤销某次提交
- `wip`：开发中，未完成的临时提交
- `release`：发布版本相关改动（如：`release: 发布v1.2.0版本`）





