import time


# 同步代码
def download(name: str, seconds: int) -> str:
    print(f"开始下载 {name}")
    time.sleep(seconds)
    print(f"下载完成 {name}")
    return name


def main() -> None:
    download("file A", 2)
    download("file B", 3)
    download("file C", 1)


main()
