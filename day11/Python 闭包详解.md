# Python 闭包详解

> 适合 Python 初学者阅读。从基础概念到常见陷阱，一步步讲透闭包。

---

## 一、前置知识：函数是一等公民

在讲闭包之前，你需要先理解 Python 中函数的一个特性——函数是「一等对象」（first-class object）。这意味着函数和数字、字符串一样，可以被赋值给变量、作为参数传递、也可以作为返回值返回。这是闭包能够存在的前提。

---

## 二、什么是闭包

简单来说，闭包是这样一种现象：

> 当一个内部函数引用了它外部函数的变量，并且这个内部函数被返回到外部使用时，即使外部函数已经执行完毕返回了，内部函数依然能「记住」并访问那些被引用的变量。

这种「带着外部环境一起走」的函数，就是闭包。

### 经典示例：计数器

```python
def make_counter():
    count = 0  # 外部函数的局部变量

    def counter():
        nonlocal count  # 引用外部变量
        count += 1
        return count

    return counter  # 返回内部函数


c1 = make_counter()
print(c1())  # 1
print(c1())  # 2
print(c1())  # 3
```

在这个例子中，`make_counter` 执行完后，按理说它的局部变量 `count` 应该随之销毁。但是因为我们返回的 `counter` 函数引用了 `count`，所以 `count` 被「绑定」到了 `counter` 上，存活了下来。每次调用 `c1()`，`count` 都会累加。

**这就是闭包的核心效果——函数携带了一份持久的状态。**

---

## 三、闭包是怎么「记住」变量的

Python 在内部用一个叫 `__closure__` 的属性来存储这些被引用的变量。你可以直接查看它：

```python
def outer():
    x = 10
    y = 20

    def inner():
        return x + y

    return inner


f = outer()
print(f.__closure__)  # (<cell at ...>, <cell at ...>)
print(f.__closure__[0].cell_contents)  # 10
print(f.__closure__[1].cell_contents)  # 20
```

每个被引用的外层变量都存在一个 `cell` 对象里。这能帮你直观地理解：

- 闭包并不是「复制」了变量的值，而是持有对 `cell` 的引用
- `cell` 指向真正的值
- 这也是为什么多个闭包可以共享同一个外部变量

---

## 四、修改闭包变量：nonlocal

在闭包里**读取**外部变量很自然，但如果你想在内部函数中**修改**外部函数的变量，就需要用到 `nonlocal` 关键字。

### 对比示例

```python
def outer():
    count = 0

    def inner_read():
        # 只是读取，没问题
        return count

    def inner_write_wrong():
        # 这样写会报错！Python 会认为你在创建一个局部变量 count
        count += 1
        return count

    def inner_write_right():
        nonlocal count  # 声明：这个 count 是外层的
        count += 1
        return count

    return inner_write_right
```

### nonlocal 是什么

`nonlocal` 是 Python 3 引入的，它的作用是告诉解释器：

> 「这个名字不是局部变量，请到外层函数作用域里找。」

### 为什么不加 nonlocal 会报错

如果不加 `nonlocal` 而直接赋值，Python 会把该名字当作内部函数的局部变量。于是在 `count += 1`（相当于 `count = count + 1`）时，因为局部 `count` 还没定义，就会报 `UnboundLocalError`。

**这是初学者最常踩的坑之一。**

---

## 五、闭包的常见用途

### 1. 状态保持

就像上面的计数器，闭包可以让函数自带「记忆」，不必依赖全局变量，比类更轻量。

```python
def make_multiplier(factor):
    def multiply(n):
        return n * factor

    return multiply


double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5))  # 10
print(triple(5))  # 15
```

### 2. 装饰器

Python 的装饰器本质上就是闭包。装饰器是一个接收函数、返回新函数的函数，返回的新函数通常引用了原函数，因此形成了闭包。

```python
def log_call(func):
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} 执行完毕")
        return result

    return wrapper


@log_call
def greet(name):
    print(f"你好，{name}")


greet("小明")
# 输出：
# 调用 greet
# 你好，小明
# greet 执行完毕
```

这里的 `wrapper` 引用了 `func`，即使 `log_call` 已经返回，`wrapper` 依然持有 `func`，这就是闭包在起作用。

### 3. 替代简单的类

当一个对象只需要保存少量状态时，用闭包往往比定义一个类更简洁。

---

## 六、一个经典陷阱：循环中的闭包

这是初学者几乎都会遇到的坑，值得特别讲一下。

### 错误示例

```python
funcs = []
for i in range(3):

    def f():
        return i

    funcs.append(f)

print(funcs[0]())  # 你可能以为是 0，实际是 2
print(funcs[1]())  # 2
print(funcs[2]())  # 2
```

### 为什么全是 2？

因为闭包持有的是**变量本身**（准确地说是 cell 引用），而不是创建那一刻的值。循环结束后 `i` 的最终值是 2，所以三个闭包看到的都是 2。

这叫做**「延迟绑定」**。

### 解决办法

用默认参数把值「固定」下来，或者再包一层函数：

```python
# 方法一：利用默认参数立即求值
def f(i=i):  # 等号右边的 i 在定义时就被求值并固定
    return i


# 方法二：用工厂函数
def make_f(i):
    def f():
        return i  # 这里的 i 是 make_f 的参数，每次调用都不同

    return f


for i in range(3):
    funcs.append(make_f(i))
```

理解了这个陷阱，你对闭包「捕获变量而非值」的本质就掌握得差不了。

---

## 七、闭包 vs 类：什么时候用哪个

闭包和类都能保存状态，选择哪个主要看复杂度。

| 场景 | 推荐方式 |
|------|----------|
| 状态简单（一两个变量），逻辑不复杂 | 闭包更轻量、更函数式 |
| 状态变多、行为变复杂，需要多个方法协同 | 用类更清晰、更好维护 |

不必强求，按场景选择即可。

---

## 八、闭包 vs 全局变量

有人会问：计数器用全局变量不也能实现吗？

确实可以，但闭包的优势在于**状态是「私有」的**：

- `count` 只能通过返回的 `counter` 函数访问
- 外部无法直接修改它
- 避免了全局变量被到处修改导致的状态混乱

这是闭包在封装上的价值。

---

## 九、要点小结

抓住这几点你就真正理解闭包了：

1. 闭包是引用了外部变量的内部函数
2. 外部函数返回后，被引用的变量不销毁，而是绑定在闭包上
3. 闭包捕获的是**变量本身**，不是值（这是延迟绑定陷阱的根源）
4. 要修改外部变量必须用 `nonlocal`
5. 装饰器是闭包最重要的应用之一

---

## 十、练习建议

把上面的代码都亲手敲一遍，尤其是这两个例子：

- **计数器**：理解状态保持
- **循环陷阱**：理解「捕获变量而非值」

运行一下、改动一下、观察输出，这样印象会深很多。闭包一开始有点绕，但只要把「变量存活」和「捕获变量而非值」这两件事想通，后面就顺了。
