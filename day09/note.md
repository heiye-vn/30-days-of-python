# Python 中的条件语句

条件语句用于让程序根据“不同情况”执行“不同代码”。

最常见的场景：

- 根据分数判断等级
- 根据年龄判断是否成年
- 根据用户名和密码判断是否登录成功
- 根据输入内容决定下一步操作

---

## 1. 什么是条件语句

条件语句的核心思想是：

> 如果条件成立，就执行一段代码；如果条件不成立，就执行另一段代码。

在 Python 中，条件语句主要使用以下关键字：

- `if`
- `elif`
- `else`

基本结构：

```python
if 条件:
    条件成立时执行的代码
```

---

## 2. `if` 语句

### 2.1 最简单的 `if`

```python
age = 20

if age >= 18:
    print("你已经成年")
```

解释：

- `age >= 18` 是一个条件表达式
- 如果结果是 `True`，就执行缩进中的代码
- 如果结果是 `False`，就跳过这段代码

---

### 2.2 `if` 的执行流程

```python
temperature = 35

if temperature > 30:
    print("天气很热")

print("程序继续执行")
```

如果条件满足，输出：

```python
天气很热
程序继续执行
```

如果条件不满足，则只输出：

```python
程序继续执行
```

注意：

- `if` 只控制它下面“缩进块”中的代码
- 条件判断结束后，程序会继续向下执行

---

## 3. `if...else` 语句

当你希望“条件成立做一件事，不成立做另一件事”时，使用 `else`。

语法：

```python
if 条件:
    条件成立时执行的代码
else:
    条件不成立时执行的代码
```

示例：

```python
age = 16

if age >= 18:
    print("你可以进入")
else:
    print("你还未成年，不能进入")
```

解释：

- `if` 分支和 `else` 分支，只会执行其中一个
- 不会两个都执行

---

## 4. `if...elif...else` 语句

当有多个条件需要判断时，可以使用 `elif`。

`elif` 是 `else if` 的缩写，表示“否则如果”。

语法：

```python
if 条件1:
    代码1
elif 条件2:
    代码2
elif 条件3:
    代码3
else:
    默认代码
```

示例：分数等级判断

```python
score = 85

if score >= 90:
    print("优秀")
elif score >= 80:
    print("良好")
elif score >= 60:
    print("及格")
else:
    print("不及格")
```

执行逻辑：

- 先判断 `score >= 90`
- 如果不成立，再判断 `score >= 80`
- 再不成立，继续判断 `score >= 60`
- 如果都不成立，就执行 `else`

注意：

- 多个分支中，只会执行第一个满足条件的分支
- 一旦某个条件满足，后面的分支就不会再判断

---

## 5. 条件表达式的结果：`True` 和 `False`

条件语句判断的本质，是看表达式结果是不是布尔值：

- `True`：真
- `False`：假

例如：

```python
print(3 > 2)     # True
print(3 < 2)     # False
print(5 == 5)    # True
print(5 != 5)    # False
```

这些表达式通常放在 `if` 后面。

---

## 6. 常见比较运算符

条件判断中最常用的是比较运算符。

| 运算符 | 含义 |
| --- | --- |
| `==` | 等于 |
| `!=` | 不等于 |
| `>` | 大于 |
| `<` | 小于 |
| `>=` | 大于等于 |
| `<=` | 小于等于 |

示例：

```python
a = 10
b = 20

print(a == b)   # False
print(a != b)   # True
print(a < b)    # True
print(a >= b)   # False
```

注意：

- `=` 是赋值
- `==` 才是比较是否相等

这是初学者最容易犯错的地方之一。

---

## 7. 逻辑运算符

有时候一个条件不够，需要多个条件组合判断。

Python 中常用的逻辑运算符有：

- `and`：并且
- `or`：或者
- `not`：取反

---

### 7.1 `and`

只有多个条件都为 `True`，结果才是 `True`。

```python
age = 20
has_ticket = True

if age >= 18 and has_ticket:
    print("可以入场")
else:
    print("不能入场")
```

---

### 7.2 `or`

只要多个条件中有一个为 `True`，结果就是 `True`。

```python
is_vip = False
balance = 1000

if is_vip or balance > 500:
    print("可以享受优惠")
else:
    print("条件不足")
```

---

### 7.3 `not`

对结果取反：

- `not True` 变成 `False`
- `not False` 变成 `True`

```python
is_raining = False

if not is_raining:
    print("可以出去玩")
```

---

## 8. 条件语句中的缩进

Python 不使用大括号 `{}` 来表示代码块，而是使用**缩进**。

例如：

```python
age = 18

if age >= 18:
    print("成年")
    print("可以办理身份证")

print("判断结束")
```

说明：

- 同一级缩进表示同一个代码块
- 一般使用 4 个空格缩进
- 缩进不正确会报错

错误示例：

```python
age = 18

if age >= 18:
print("成年")
```

这会触发缩进错误。

---

## 9. 嵌套条件语句

条件语句中还可以继续写条件语句，这叫嵌套。

示例：

```python
age = 20
has_id = True

if age >= 18:
    if has_id:
        print("可以进入")
    else:
        print("请先出示身份证")
else:
    print("未成年不能进入")
```

执行逻辑：

1. 先判断是否成年
2. 如果成年，再判断是否有证件
3. 如果未成年，直接执行外层 `else`

嵌套可以实现复杂逻辑，但不要嵌套过深，否则代码会难读。

---

## 10. 多条件判断的顺序很重要

条件的顺序会影响结果。

看下面这个例子：

```python
score = 95

if score >= 60:
    print("及格")
elif score >= 90:
    print("优秀")
```

输出结果是：

```python
及格
```

原因：

- `score = 95` 先满足了 `score >= 60`
- 程序已经进入这个分支
- 后面的 `elif score >= 90` 不会再执行

正确写法应该把范围更高、更严格的条件放前面：

```python
score = 95

if score >= 90:
    print("优秀")
elif score >= 60:
    print("及格")
```

---

## 11. 条件判断中常见的“真值”

在 Python 中，不只是 `True` 和 `False` 可以用于条件判断，很多对象本身也可以表示“真”或“假”。

通常以下值会被当作 `False`：

- `False`
- `None`
- `0`
- `0.0`
- `''`（空字符串）
- `[]`（空列表）
- `()`（空元组）
- `{}`（空字典）
- `set()`（空集合）

其余大多数值都会被当作 `True`。

示例：

```python
name = ""

if name:
    print("用户名不为空")
else:
    print("用户名为空")
```

再例如：

```python
numbers = [1, 2, 3]

if numbers:
    print("列表不为空")
```

这种写法在 Python 中非常常见。

---

## 12. 三元表达式

如果条件判断非常简单，可以写成一行。

语法：

```python
值1 if 条件 else 值2
```

示例：

```python
age = 20
result = "成年" if age >= 18 else "未成年"
print(result)
```

它等价于：

```python
if age >= 18:
    result = "成年"
else:
    result = "未成年"
```

适用场景：

- 简单赋值
- 简单返回值

不建议在逻辑复杂时使用，否则可读性会变差。

---

## 13. 条件语句常见错误

### 13.1 把 `=` 写成 `==`

错误理解：

- `=` 是“比较”

正确理解：

- `=` 是赋值
- `==` 才是比较是否相等

错误示例：

```python
age = 18

if age = 18:
    print("成年")
```

这会报语法错误。

正确写法：

```python
if age == 18:
    print("成年")
```

---

### 13.2 条件顺序写错

错误示例：

```python
score = 92

if score >= 60:
    print("及格")
elif score >= 90:
    print("优秀")
```

因为先匹配到了 `>= 60`，所以得不到“优秀”。

---

### 13.3 缩进不一致

错误示例：

```python
if True:
    print("hello")
      print("world")
```

缩进层级不一致会导致报错。

---

### 13.4 条件永远为真或永远为假

例如：

```python
if 10:
    print("这行会执行")
```

因为 `10` 会被当作真值，所以这段代码总会执行。

这不是语法错误，但有时候不是你真正想表达的逻辑。

---

## 14. 实际示例

### 14.1 判断奇偶数

```python
num = 7

if num % 2 == 0:
    print("偶数")
else:
    print("奇数")
```

---

### 14.2 判断登录

```python
username = "admin"
password = "123456"

if username == "admin" and password == "123456":
    print("登录成功")
else:
    print("用户名或密码错误")
```

---

### 14.3 判断闰年

闰年规则：

- 能被 400 整除，是闰年
- 或者能被 4 整除但不能被 100 整除，也是闰年

```python
year = 2024

if year % 400 == 0 or (year % 4 == 0 and year % 100 != 0):
    print("闰年")
else:
    print("平年")
```

这个例子说明：

- 条件语句可以配合逻辑运算符写出较复杂的规则
- 括号可以让逻辑更清晰

---

## 15. `if` 语句的完整结构总结

### 15.1 单分支

```python
if 条件:
    代码
```

---

### 15.2 双分支

```python
if 条件:
    代码1
else:
    代码2
```

---

### 15.3 多分支

```python
if 条件1:
    代码1
elif 条件2:
    代码2
elif 条件3:
    代码3
else:
    代码4
```

---

### 15.4 嵌套分支

```python
if 条件1:
    if 条件2:
        代码
    else:
        代码
else:
    代码
```

---

## 16. 编写条件语句的建议

- 先写清楚你要判断的规则
- 把范围更严格、更特殊的条件放前面
- 尽量避免嵌套太深
- 使用括号增强逻辑表达的清晰度
- 变量名尽量见名知意，比如 `is_login`、`has_ticket`、`score`
- 简单逻辑可以用三元表达式，复杂逻辑仍然优先使用普通 `if`

---

## 17. 练习题

### 练习 1：判断正负数

要求：输入一个数字，判断它是正数、负数还是 0。

参考代码：

```python
num = int(input("请输入一个数字："))

if num > 0:
    print("正数")
elif num < 0:
    print("负数")
else:
    print("0")
```

---

### 练习 2：判断成绩等级

要求：

- 90 分及以上：A
- 80~89：B
- 70~79：C
- 60~69：D
- 60 以下：E

参考代码：

```python
score = int(input("请输入成绩："))

if score >= 90:
    print("A")
elif score >= 80:
    print("B")
elif score >= 70:
    print("C")
elif score >= 60:
    print("D")
else:
    print("E")
```

---

### 练习 3：判断是否能买票

要求：

- 年龄大于等于 18，且有身份证，才可以买票

参考代码：

```python
age = int(input("请输入年龄："))
has_id = input("是否有身份证（yes/no）：")

if age >= 18 and has_id == "yes":
    print("可以买票")
else:
    print("不可以买票")
```

---

### 练习 4：猜数字范围

要求：输入一个数字，判断：

- 小于 10
- 在 10 到 50 之间
- 大于 50

参考代码：

```python
num = int(input("请输入一个数字："))

if num < 10:
    print("小于 10")
elif num <= 50:
    print("在 10 到 50 之间")
else:
    print("大于 50")
```

---

## 18. 本章小结

这一章你需要掌握的重点有：

- `if` 用来做单条件判断
- `if...else` 用来做二选一判断
- `if...elif...else` 用来做多分支判断
- 条件表达式的结果是 `True` 或 `False`
- 比较运算符和逻辑运算符是条件判断的基础
- Python 使用缩进表示代码块
- 条件顺序会影响最终结果
- 可以使用嵌套条件和三元表达式，但要注意可读性

如果把条件语句学扎实，后面学习循环、函数、项目练习时会轻松很多。
