import argparse


def main():
    # 1. 创建解析器对象，添加工具描述
    parser = argparse.ArgumentParser(description="这是一个计算数字平方的命令行工具")

    # 2. 添加一个位置参数（必填，必须是整数）
    parser.add_argument("number", type=int, help="要计算平方的数字")

    # 3. 添加一个可选参数（开关，如果命令行传入则为 True，默认为 False）
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="输出详细的描述信息"
    )

    # 4. 解析命令行传入的参数
    args = parser.parse_args()

    result = args.number**2

    # 5. 根据参数执行不同的逻辑
    if args.verbose:
        print(f"输入数字 {args.number} 的平方计算结果是：{result}")
    else:
        print(result)


if __name__ == "__main__":
    main()
