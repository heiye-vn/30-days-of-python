"""
案例：读取文件、统计单词、记录耗时
"""

from collections.abc import Iterable
from contextlib import contextmanager
from pathlib import Path
from time import perf_counter
from typing import TypedDict


class WordStats(TypedDict):
    total: int
    unique: int


@contextmanager
def timer(label: str):
    start = perf_counter()
    try:
        yield
    finally:
        elapsed = perf_counter() - start
        print(f"{label} 耗时：{elapsed:.4f} 秒")


def read_words(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return text.split()


def calculate_stats(words: Iterable[str]) -> WordStats:
    word_list = list(words)
    return {"total": len(word_list), "unique": len(set(word_list))}


def main() -> None:
    path = Path("article.txt")

    with timer("统计单词"):
        words = read_words(path)
        stats = calculate_stats(words)

    print(f"总词数：{stats['total']}")
    print(f"不重复词数：{stats['unique']}")


if __name__ == "__main__":
    main()
