"""
Python 包管理工具实战练习
本文件通过实际操作演示各包管理工具的核心用法。
建议在虚拟环境中运行，避免污染系统 Python。
"""

import os
import subprocess
import sys


def run_command(cmd: str, description: str) -> None:
    """运行命令并打印结果"""
    print(f"\n{'=' * 60}")
    print(f"[>] {description}")
    print(f"    命令: {cmd}")
    print(f"{'=' * 60}")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        if result.stdout:
            print(f"    输出:\n{result.stdout[:500]}")
        if result.returncode != 0 and result.stderr:
            print(f"    错误:\n{result.stderr[:300]}")
    except subprocess.TimeoutExpired:
        print("    [!] 命令超时（30秒）")


def section(title: str) -> None:
    """打印章节标题"""
    print(f"\n{'#' * 60}")
    print(f"  {title}")
    print(f"{'#' * 60}")


# ============================================================
# 第一部分：pip 基础操作
# ============================================================

section("第一部分：pip 基础操作")

# 1.1 查看当前 Python 环境信息
run_command(f"{sys.executable} -m pip --version", "查看 pip 版本")

# 1.2 查看已安装的包（只取前 20 行演示）
run_command(
    f"{sys.executable} -m pip list --format=columns 2>nul", "查看已安装的包（列表形式）"
)

# 1.3 查看某个包的详细信息
run_command(f"{sys.executable} -m pip show pip", "查看 pip 包自身的详细信息")

# 1.4 检查哪些包可以升级（可能耗时较长）
run_command(f"{sys.executable} -m pip list --outdated 2>nul", "检查可升级的包")

# ============================================================
# 第二部分：虚拟环境操作
# ============================================================

section("第二部分：虚拟环境（venv）")

venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_venv")

# 2.1 创建虚拟环境
print(f"\n[>] 创建虚拟环境: {venv_path}")
if not os.path.exists(venv_path):
    run_command(f"{sys.executable} -m venv {venv_path}", "创建虚拟环境")
    print("    [OK] 虚拟环境创建成功！")
else:
    print("    [SKIP] 虚拟环境已存在，跳过创建")

# 2.2 展示虚拟环境结构
print("\n[>] 虚拟环境目录结构：")
if os.path.exists(venv_path):
    for item in sorted(os.listdir(venv_path)):
        print(f"    {item}/")

# ============================================================
# 第三部分：检查工具是否安装
# ============================================================

section("第三部分：检查各工具安装状态")

tools = ["pip", "pipx", "poetry", "uv", "pipenv", "conda"]

for tool in tools:
    try:
        result = subprocess.run(
            [tool, "--version"], capture_output=True, text=True, timeout=5
        )
        version = result.stdout.strip() or result.stderr.strip()
        print(f"    [OK] {tool:12s} -> {version}")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print(f"    [--] {tool:12s} -> 未安装")

# ============================================================
# 第四部分：依赖文件实践
# ============================================================

section("第四部分：依赖文件操作")

# 4.1 生成 requirements.txt 示例
sample_requirements = """\
# requirements.txt 示例
# 直接依赖
requests>=2.31.0
fastapi>=0.110.0
uvicorn>=0.27.0

# 开发依赖（通常放在 requirements-dev.txt）
# pytest>=8.0.0
# ruff>=0.3.0
"""

req_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "requirements-example.txt"
)
with open(req_file, "w", encoding="utf-8") as f:
    f.write(sample_requirements)
print(f"\n[>] 已生成示例文件: {req_file}")

# 4.2 解析 requirements.txt
print("\n[>] 解析 requirements.txt 中的依赖：")
with open(req_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            print(f"    - {line}")

# ============================================================
# 第五部分：pyproject.toml 示例
# ============================================================

section("第五部分：pyproject.toml 示例")

sample_pyproject = """\
# pyproject.toml 示例（Poetry / uv 风格）
[project]
name = "my-day20-project"
version = "0.1.0"
description = "Day 20 包管理学习项目"
requires-python = ">=3.11"

dependencies = [
    "requests>=2.31.0",
    "fastapi>=0.110.0",
    "uvicorn>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
]

[tool.ruff]
line-length = 88
select = ["E", "F", "I"]
"""

toml_file = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "pyproject-example.toml"
)
with open(toml_file, "w", encoding="utf-8") as f:
    f.write(sample_pyproject)
print(f"\n[>] 已生成示例文件: {toml_file}")
print("\n[>] pyproject.toml 是现代 Python 项目的标准配置文件")
print("    它统一了：项目元数据 + 依赖声明 + 工具配置")

# ============================================================
# 第六部分：工具选择决策
# ============================================================

section("第六部分：工具选择速查")

recommendations = {
    "学习 / 小脚本": "pip + venv",
    "FastAPI Web 项目": "uv 或 Poetry",
    "AI/ML 项目": "conda + uv",
    "CLI 工具发布": "Poetry 或 uv",
    "企业级项目": "uv（统一团队工具链）",
}

print("\n[>] 项目类型 -> 推荐工具：")
for project_type, tool in recommendations.items():
    print(f"    {project_type:20s} -> {tool}")

# ============================================================
# 总结
# ============================================================

section("完成！")
print("""
恭喜你完成了 Day 20 的学习！

本练习生成的文件：
  - requirements-example.txt  （依赖文件示例）
  - pyproject-example.toml    （项目配置示例）
  - test_venv/                （测试虚拟环境）

下一步建议：
  1. 安装 uv：powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  2. 用 uv 创建一个真实项目：uv init my-project
  3. 体验 uv 的速度：uv add requests

延伸阅读：
  - uv 官方文档：https://docs.astral.sh/uv/
  - Poetry 官方文档：https://python-poetry.org/docs/
  - PEP 621（pyproject.toml 标准）：https://peps.python.org/pep-0621/
""")
