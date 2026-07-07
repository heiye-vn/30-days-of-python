"""
面向对象建模实战：需求 → 类图 → 实现

本模块实现了一个简易的图书管理系统，用于演示面向对象设计（OOD）中的类设计、
组合/聚合/关联/依赖/继承等关系，以及 Python 数据类（dataclass）与枚举（Enum）的实际应用。
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

"""
需求分析：
开发一个简易图书管理系统：用户可以搜索图书、借阅图书、归还图书。
系统需要记录借阅历史，超期未还要收取罚款。管理员可以添加图书、查看借阅统计

类与类之间的关系：
Library 拥有多个 Book -> 组合关系
Library 管理多个 BorrowRecord -> 聚合关系
User 产生 BorrowRecord -> 关联关系
BorrowRecord 引用 Book -> 依赖关系
Admin is-a User -> 继承关系
"""


class BookStatus(Enum):
    """图书状态枚举

    定义了图书在馆内的三种可能状态。
    """
    AVAILABLE = "可借"      # 图书在馆，可供借阅
    BORROWED = "已借出"    # 图书已被借出
    LOST = "遗失"          # 图书已遗失，不可借阅


@dataclass
class Book:
    """图书实体类

    使用 dataclass 自动生成构造函数、表示方法等。
    """
    isbn: str               # 图书的唯一标识符 (ISBN)
    title: str              # 图书标题
    author: str             # 图书作者
    status: BookStatus = BookStatus.AVAILABLE  # 图书当前状态，默认为可借
    daily_fine: float = 0.5  # 每日逾期罚款金额，默认为 0.5 元/天

    def __str__(self):
        """返回图书的可读字符串表示"""
        return f"《{self.title}》({self.author}) [{self.status.value}]"


@dataclass
class BorrowRecord:
    """借阅记录实体类

    记录单次借阅的详细信息，并负责逾期状态判断和罚款金额的计算。
    """
    book: Book                                          # 被借阅的图书对象 (依赖/关联关系)
    borrower_name: str                                  # 借阅者姓名
    borrower_date: datetime = field(default_factory=datetime.now)  # 借阅时间，默认为当前系统时间
    due_days: int = 14                                  # 允许借阅的天数，默认 14 天
    return_date: datetime = None                        # 归还时间，未归还时为 None

    @property
    def due_date(self) -> datetime:
        """计算图书的应归还日期"""
        return self.borrower_date + timedelta(days=self.due_days)

    @property
    def is_overdue(self) -> bool:
        """检查该借阅记录是否已逾期

        如果已归还，比较归还时间与应还时间；如果未归还，比较当前时间与应还时间。
        """
        if self.return_date:
            return self.return_date > self.due_date
        return datetime.now() > self.due_date

    @property
    def fine_amount(self) -> float:
        """计算当前的罚款金额

        罚款金额 = 逾期天数 * 每日罚款标准。未逾期时返回 0.0。
        """
        if not self.is_overdue:
            return 0.0
        end = self.return_date or datetime.now()
        overdue_days = (end - self.due_date).days
        # 注意：使用 datetime 相减得到的 timedelta.days 会截断不足一天的部分，
        # 如果需要将不足一天的情况也计入一天罚款，可以使用向上取整的计算逻辑。
        return overdue_days * self.book.daily_fine

    def return_book(self):
        """执行归还图书操作

        设置归还时间为当前时间，并将图书的状态恢复为可借。
        """
        self.return_date = datetime.now()
        self.book.status = BookStatus.AVAILABLE


class Library:
    """图书馆类

    系统核心协调者，负责维护馆藏图书列表、借阅记录列表，并提供图书的增、删、改、查、借、还及统计等核心业务逻辑。
    """

    def __init__(self, name: str):
        """初始化图书馆实例

        Args:
            name: 图书馆名称
        """
        self.name = name
        self._books: dict[str, Book] = {}  # 馆藏图书字典，键为 ISBN，值为 Book 对象
        self._records: list[BorrowRecord] = []  # 借阅历史记录列表

    def add_book(self, book: Book):
        """向图书馆添加新书

        Args:
            book: 待添加的 Book 实例
        """
        self._books[book.isbn] = book

    def search(self, keyword: str) -> list[Book]:
        """根据关键词模糊搜索图书

        在图书标题和作者中搜索包含该关键词（不区分大小写）的图书。

        Args:
            keyword: 搜索关键词

        Returns:
            符合搜索条件的图书列表
        """
        keyword = keyword.lower()
        return [
            b
            for b in self._books.values()
            if keyword in b.title.lower() or keyword in b.author.lower()
        ]

    def borrow(self, isbn: str, borrower: str) -> BorrowRecord:
        """借阅图书业务逻辑

        1. 检查图书是否存在。
        2. 检查图书当前是否可借（状态是否为 AVAILABLE）。
        3. 更新图书状态为 BORROWED。
        4. 创建并记录 BorrowRecord。

        Args:
            isbn: 待借图书的 ISBN
            borrower: 借阅人姓名

        Returns:
            生成的 BorrowRecord 借阅记录实例
        """
        book = self._books.get(isbn)
        if not book:
            raise ValueError(f"图书 {isbn} 不存在")
        if book.status != BookStatus.AVAILABLE:
            raise ValueError(f"{book.title} 当前不可借")

        book.status = BookStatus.BORROWED
        record = BorrowRecord(book=book, borrower_name=borrower)
        self._records.append(record)
        return record

    def return_book(self, isbn: str) -> dict:
        """归还图书业务逻辑

        反向查找最近一条关于该 ISBN 且未归还的借阅记录，执行归还操作并计算罚款。

        Args:
            isbn: 待归还图书的 ISBN

        Returns:
            包含借阅记录对象(record)和罚款金额(fine)的字典
        """
        for record in reversed(self._records):
            if record.book.isbn == isbn and record.return_date is None:
                record.return_book()
                fine = record.fine_amount
                return {"record": record, "fine": fine}
        raise ValueError(f"未找到 {isbn} 的借阅记录")

    def get_statistics(self) -> dict:
        """获取图书馆的借阅统计数据

        统计项包括：总借阅次数、当前逾期未还的记录数、累计收取的罚款金额以及馆藏图书总量。

        Returns:
            包含各项统计数据的字典
        """
        total_borrow = len(self._records)
        overdue = sum(1 for r in self._records if r.is_overdue and not r.return_date)
        total_fines = sum(r.fine_amount for r in self._records)
        return {
            "总借阅次数：": total_borrow,
            "当前逾期未还": overdue,
            "累计罚款": total_fines,
            "馆藏图书": len(self._books),
        }


# ==========================================
# 使用演示
# ==========================================
if __name__ == "__main__":
    # 实例化图书馆
    lib = Library("国家图书馆")
    
    # 向图书馆添加图书
    lib.add_book(Book("978-0-1", "Python 编程", "Guido"))
    lib.add_book(Book("978-0-2", "算法导论", "CLRS"))
    lib.add_book(Book("978-0-3", "西游记", "罗贯中"))

    # 模拟用户借书
    print("--- 借书测试 ---")
    record = lib.borrow("978-0-1", "张三")
    print(f"借阅记录: {record}")

    # 模拟用户还书
    print("\n--- 还书测试 ---")
    result = lib.return_book("978-0-1")
    print(f"归还成功，罚款: {result['fine']} 元")
    
    # 打印当前图书馆的借阅统计信息
    print("\n--- 统计信息 ---")
    print(lib.get_statistics())

