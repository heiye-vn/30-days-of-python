# 实例：安全地读取文件
def read_config(filepath):
    import json
    file = None
    try:
        file = open(filepath, "r", encoding="utf-8")
        content = file.read()
        config_data = json.loads(content)
    except FileNotFoundError:
        print(f"配置文件不存在：{filepath}")
        return {}
    except PermissionError:
        print(f"没有权限读取文件：{filepath}")
        return {}
    except json.JSONDecodeError:
        print(f"配置文件格式错误（非有效 JSON）：{filepath}")
        return {}
    else:
        # 只有在 try 块中所有代码（包括文件读取和 JSON 解析）成功执行时才执行
        print("配置文件读取成功！")
        return config_data
    finally:
        # 无论如何都要关闭文件（即使发生了异常）
        if file is not None:
            file.close()
            print("文件已关闭")


"""
更好的写法（使用 with 语句）
with：上下文管理器，确保资源自动管理（文件关闭、锁释放等），无需 finally
"""


def read_config_better(filepath):
    import json
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
            config_data = json.loads(content)
    except (FileNotFoundError, PermissionError) as e:
        print(f"读取失败：{e}")
        return {}
    else:
        print("配置文件读取成功！")
        return config_data


# 测试读取新创建的 config.json 配置文件
if __name__ == "__main__":
    import os

    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_dir, "config.json")

    print("--- 开始测试读取配置文件 ---")
    config = read_config_better(config_file_path)
    print("解析出的配置数据：", config)
