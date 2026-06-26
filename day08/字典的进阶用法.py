"""
字典的高级用法
"""

from collections import defaultdict, OrderedDict, Counter, ChainMap
from types import MappingProxyType

"""
setdefault() 与 collections.defaultdict
处理“键可能不存在，但需要初始化并追加数据”的场景（比如分组计数）
"""
# 场景：统计各部门的员工
tasks = [("Tech", "Alex"), ("HR", "Jane"), ("Tech", "Bob")]
groups = {}

# 方法一：使用字典的 setdefault() 方法
for dept, name in tasks:
    groups.setdefault(dept, []).append(name)
# print(groups)

# 方法二：使用 defaultdict() 【推荐】
groups_default = defaultdict(list)  # 默认工厂函数为 list
# print(type(groups_default))  # <class 'collections.defaultdict'>
for dept, name in tasks:
    groups_default[dept].append(name)
groups_default = dict(groups_default)  # 转换为普通字典
# print(groups_default)


"""
defaultdict（默认字典） —— 自动初始化
"""
# 统计词频：无需手动检查键是否存在
word_count = defaultdict(int)
for word in ["apple", "banana", "apple", "cherry", "banana", "apple"]:
    word_count[word] += 1
# print(word_count)

# 分组：值为列表
groups_ = defaultdict(list)
students = [("A班", "Alice"), ("B班", "Bob"), ("A班", "Charlie")]
for cls, name in students:
    groups_[cls].append(name)
# print(groups_)


"""
OrderedDict（有序字典） —— 显式有序 + 额外能力
"""
od = OrderedDict([("a", 1), ("b", 2), ("c", 3)])
od.move_to_end("a")  # 移到末尾
# print(od)
od.move_to_end("c", last=False)  # 移动到开头
# print(od)

# OrderedDict 对插入顺序比较严格
isEqual = OrderedDict([("a", 1), ("b", 2)]) == OrderedDict([("b", 2), ("a", 1)])
# print(isEqual)
isEqual_ = {"a": 1, "b": 2} == {"b": 2, "a": 1}
# print(isEqual_)


"""
Counter —— 计数器
"""
c = Counter("abracadabra")
# print(c)
# print(c.most_common(2))  # most_common() 返回一个列表，包含最常见的 n 个元素
# print(c.total())  # total() 返回计数器中元素的总数
new_c = Counter(a=3, b=1) + Counter(a=1, b=2)  # 计数器相加
# print(new_c)


"""
ChainMap（链式映射） —— 多字典链式查找
应用场景：配置层级管理（命令行参数 > 环境变量 > 配置文件 > 默认值）
"""
defaults = {"color": "red", "size": "M"}
user_prefs = {"color": "blue"}
config = ChainMap(user_prefs, defaults)
# print(config)
# print(config["color"])
# print(config["size"])


"""
MappingProxyType —— 只读字典视图
应用场景：保护模块级常量字典、类属性不被意外修改
"""
original = {"key": "value", "name": "王麻子"}
readonly = MappingProxyType(original)
# readonly["name"] = "孙云" # TypeError，只读字典无法修改
print(readonly)
original["name"] = "王林"
print(original)

"""
总结：
需要普通映射          → dict
需要自动初始化        → defaultdict
需要计数/Top-N       → Counter
需要调整顺序/顺序敏感比较 → OrderedDict
需要多层配置查找      → ChainMap
需要只读保护          → MappingProxyType
需要固定字段结构      → dataclass / NamedTuple / TypedDict
"""
