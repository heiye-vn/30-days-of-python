import tempfile
from pathlib import Path

# 创建临时文件，delete=False 表示不自动删除文件
# with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
#     f.write("临时数据")
#     temp_path = f.name
#     print(f"临时文件：{temp_path}")

# 手动删除
# Path(temp_path).unlink()


# 创建临时目录
# with tempfile.TemporaryDirectory() as tmpdir:
#     print(f"临时目录：{tmpdir}")
#     temp_file = Path(tmpdir) / "test.txt"
#     temp_file.write_text("Hello", encoding="utf-8")
# with 块结束后自动删除目录及其内容

# SpooledTemporaryFile（内存+磁盘混合）
# with tempfile.SpooledTemporaryFile(max_size=1024 * 1024) as f:
#     f.write(b"large data...")
