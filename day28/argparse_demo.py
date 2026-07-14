"""
argparse：Python 内置的标准库模块，专门用于解析命令行参数和选项
"""

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
