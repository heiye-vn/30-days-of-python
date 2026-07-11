"""
生成器（Generator）
"""

"""
生成器是一种特殊的迭代器

生成器函数 vs 普通函数

生成器函数使用 yield 关键字，普通函数使用 return 关键字

普通函数执行：调用 → 运行 → return → 结束
生成器函数执行：调用 → 运行到yield → 暂停 → 再次next() → 继续执行

"""


def simple_generator():
    yield 1
    yield 2
    yield 3


gen = simple_generator()

# print(next(gen))
# print(next(gen))
# print(next(gen))
# print(next(gen))  # 抛出 StopIteration 异常


""" yield 执行过程 """


def test():
    print("开始")
    yield "A"

    print("继续")
    yield "B"

    print("结束")


gen_ = test()
# print(next(gen_))
# print(next(gen_))
# print(next(gen_))


"""
生成器表达式（用小括号）
"""
squares = (x * x for x in range(5))
# print(squares)

# for value in squares:
#     print(value)


"""
生成器的使用场景：
- 大文件逐行读取
- 大量数据逐条处理
- 无限序列
- 数据管道
- 不需要一次性拿到全部结果
"""


def read_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            yield line.strip()


# for line in read_lines("data.txt"):
#     print(line)


# 生成斐波那契数列
def fibonacci(limit):
    a, b = 0, 1
    count = 0
    while count < limit:
        yield a
        a, b = b, a + b
        count += 1


# for num in fibonacci(5):
#     print(num)


"""
生成器在 RAG 中的应用
"""


def chunk_documents(text, chunk_size=500, overlap=50):
    """把长文档切成chunk，惰性生成，不用一次性把所有 chunk 放进内存"""
    start = 0
    while start < len(text):
        yield text[start : start + chunk_size]
        start += chunk_size - overlap


def batch_embeddings(chunks, batch_size=16):
    """把 chunk 流按 batch 打包，方便 embedding API"""
    batch = []
    for chunk in chunks:
        batch.append(chunk)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:  # 处理最后不满一批的余量
        yield batch


# 整个链路都是惰性的：读文件 → 切分 → 打批 → 逐批调用 embedding API 写入 pgvector
# 伪代码：
# for batch in batch_embeddings(chunk_documents(long_text)):
#     embeddings = call_embedding_api(batch)
#     insert_into_pgvector(batch, embeddings)
