# 30 Days of Python 学习项目 🐍

本项目用于记录在 30 天 Python 学习旅程中的代码练习与实战。

## 📁 目录结构

```text
.
├── .gitignore          # Git 忽略文件配置
├── README.md           # 项目自述文档
└── day01/              # 第 1 天的练习与小游戏
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
