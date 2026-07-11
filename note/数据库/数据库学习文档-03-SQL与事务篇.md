# 数据库学习文档 - 第 03 篇：SQL 与事务篇

> 面向"前端转后端 Python 开发者"的数据库学习文档
> 适用读者：已掌握 Node.js 版 LangChain/LangGraph，正在学习后端 Python（FastAPI/LangChain 方向）
> 运行环境：Windows（cmd.exe，注意 GBK 编码问题，代码中不使用 emoji）

---

## 第五章 SQL 进阶查询

在前两篇中，我们掌握了表设计和基础 CRUD。本章进入真正的"后端 SQL 力"训练：多表连接、子查询、聚合分组、窗口函数、CTE，以及 MySQL 与 PostgreSQL 的语法差异。这些是写报表、做数据分析、优化查询的基础。

> 前端类比：如果基础 CRUD 相当于前端的"增删改查表单"，那么进阶查询就相当于"复杂数据加工管道"——你不再只是取一条数据，而是要像 RxJS 的管道操作符一样，把多张表 join、filter、group、window 串联起来，一次性算出业务需要的结果。

### 5.1 多表连接（JOIN）

实际业务中数据分散在多张表（用户表、商品表、订单表、订单详情表），JOIN 是把它们按关联条件拼接成一张"宽表"的手段。理解 JOIN 的关键是搞清楚"以哪张表为基准"以及"匹配不上的行如何处理"。

先建立数据库表结构以便后续演示。假设我们有一个电商系统，包含用户表、商品表、订单表和订单详情表。

```sql
-- ==============================
-- MySQL 版本建表
-- ==============================
CREATE DATABASE IF NOT EXISTS shop_demo
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE shop_demo;

CREATE TABLE users (
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  username    VARCHAR(64)  NOT NULL,
  email       VARCHAR(128) NOT NULL,
  created_at  DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3)
) ENGINE=InnoDB;

CREATE TABLE products (
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  name        VARCHAR(128) NOT NULL,
  price       DECIMAL(10,2) NOT NULL,
  stock       INT          NOT NULL DEFAULT 0,
  category    VARCHAR(64)
) ENGINE=InnoDB;

CREATE TABLE orders (
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id     BIGINT       NOT NULL,
  status      VARCHAR(16)  NOT NULL DEFAULT 'CREATED',
  created_at  DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE order_items (
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_id    BIGINT       NOT NULL,
  product_id  BIGINT       NOT NULL,
  quantity    INT          NOT NULL,
  unit_price  DECIMAL(10,2) NOT NULL,
  CONSTRAINT fk_items_order   FOREIGN KEY (order_id)   REFERENCES orders(id),
  CONSTRAINT fk_items_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB;
```

```sql
-- ==============================
-- PostgreSQL 版本建表
-- ==============================
CREATE DATABASE shop_demo
  WITH ENCODING 'UTF8';

\c shop_demo

CREATE TABLE users (
  id          BIGSERIAL PRIMARY KEY,
  username    VARCHAR(64)  NOT NULL,
  email       VARCHAR(128) NOT NULL,
  created_at  TIMESTAMPTZ(3) NOT NULL DEFAULT NOW()
);

CREATE TABLE products (
  id          BIGSERIAL PRIMARY KEY,
  name        VARCHAR(128) NOT NULL,
  price       NUMERIC(10,2) NOT NULL,
  stock       INT          NOT NULL DEFAULT 0,
  category    VARCHAR(64)
);

CREATE TABLE orders (
  id          BIGSERIAL PRIMARY KEY,
  user_id     BIGINT       NOT NULL REFERENCES users(id),
  status      VARCHAR(16)  NOT NULL DEFAULT 'CREATED',
  created_at  TIMESTAMPTZ(3) NOT NULL DEFAULT NOW()
);

CREATE TABLE order_items (
  id          BIGSERIAL PRIMARY KEY,
  order_id    BIGINT       NOT NULL REFERENCES orders(id),
  product_id  BIGINT       NOT NULL REFERENCES products(id),
  quantity    INT          NOT NULL,
  unit_price  NUMERIC(10,2) NOT NULL
);
```

接下来向四张表写入示例数据，后续所有查询都基于这批数据。

```sql
-- ==============================
-- 示例数据（MySQL / PostgreSQL 通用）
-- ==============================
INSERT INTO users(username, email) VALUES
  ('alice',  'alice@example.com'),
  ('bob',    'bob@example.com'),
  ('carol',  'carol@example.com'),
  ('dave',   'dave@example.com');

INSERT INTO products(name, price, stock, category) VALUES
  ('iPhone 15',      7999.00, 100, 'phone'),
  ('MacBook Pro',   14999.00,  50, 'laptop'),
  ('AirPods Pro',    1899.00, 200, 'accessory'),
  ('iPad Air',       4399.00,  80, 'tablet'),
  ('Magic Mouse',     399.00,   0, 'accessory');

-- alice 下了两个订单，bob 下了一个，carol/dave 暂未下单
INSERT INTO orders(user_id, status) VALUES
  (1, 'PAID'), (1, 'CREATED'), (2, 'PAID');

-- 订单1（alice）：iPhone + AirPods；订单2（alice）：MacBook；订单3（bob）：iPad
INSERT INTO order_items(order_id, product_id, quantity, unit_price) VALUES
  (1, 1, 1, 7999.00),
  (1, 3, 2, 1899.00),
  (2, 2, 1, 14999.00),
  (3, 4, 1, 4399.00);
```

#### 5.1.1 INNER JOIN

`INNER JOIN`（内连接）只返回两张表中满足连接条件的行，可以理解为两个集合的"交集"。

> 前端类比：INNER JOIN 类似于 JavaScript 中根据相同 id 合并两个数组。比如你有 `users` 数组和 `orders` 数组，用 `orders.filter(o => users.some(u => u.id === o.userId))` 后再 map 出对应 user，本质上就是内连接——只保留能匹配上的记录。

业务场景：查询"已下单的用户及其订单信息"。carol 和 dave 没有订单，所以不会出现在结果中。

```sql
-- MySQL / PostgreSQL 通用
SELECT
    u.id            AS user_id,
    u.username,
    o.id            AS order_id,
    o.status,
    o.created_at
FROM users u
INNER JOIN orders o ON u.id = o.user_id
ORDER BY u.id, o.id;
```

执行结果（示意）：

```
user_id | username | order_id | status   | created_at
--------+----------+----------+----------+---------------------
   1    | alice    |    1     | PAID     | 2024-01-01 10:00:00
   1    | alice    |    2     | CREATED  | 2024-01-01 11:00:00
   2    | bob      |    3     | PAID     | 2024-01-01 12:00:00
```

多表 INNER JOIN 链式连接：查询"每个订单详情中包含的商品名、数量、单价、小计"。

```sql
-- MySQL / PostgreSQL 通用
SELECT
    o.id       AS order_id,
    u.username,
    p.name     AS product_name,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS subtotal
FROM orders o
INNER JOIN users        u  ON o.user_id    = u.id
INNER JOIN order_items  oi ON oi.order_id  = o.id
INNER JOIN products     p  ON oi.product_id = p.id
ORDER BY o.id, p.name;
```

#### 5.1.2 LEFT JOIN

`LEFT JOIN`（左连接）以左表为基准，返回左表所有行，即使右表没有匹配。右表无匹配时，右表字段为 NULL。它也叫 `LEFT OUTER JOIN`，OUTER 关键字可省略。

> 前端类比：LEFT JOIN 类似于遍历左数组，对每个元素去右数组找匹配，找不到就补一个空对象。比如 `users.map(u => ({ ...u, order: orders.find(o => o.userId === u.id) || null }))`，每个用户都会出现，没下单的用户 order 字段为 null。

业务场景：查询"所有用户及其订单情况（包括没下单的用户）"。carol 和 dave 没有订单，但仍会出现，order 字段为 NULL。

```sql
-- MySQL / PostgreSQL 通用
SELECT
    u.id       AS user_id,
    u.username,
    o.id       AS order_id,
    o.status
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
ORDER BY u.id, o.id;
```

执行结果（示意）：

```
user_id | username | order_id | status
--------+----------+----------+--------
   1    | alice    |    1     | PAID
   1    | alice    |    2     | CREATED
   2    | bob      |    3     | PAID
   3    | carol    |   NULL   | NULL
   4    | dave     |   NULL   | NULL
```

实战技巧：利用 LEFT JOIN 产生的 NULL 行，可以查找"从未下过单的用户"。

```sql
-- MySQL / PostgreSQL 通用
SELECT u.id, u.username
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;
-- 结果：carol、dave
```

这种"IS NULL 反查"模式在后端非常常用，比如"未读消息用户""未打卡员工""未关联标签的商品"等都用同一套路。

#### 5.1.3 RIGHT JOIN 与 FULL JOIN

`RIGHT JOIN`（右连接）以右表为基准，返回右表所有行。实际开发中较少使用，通常习惯把主表放左边，直接改写为 LEFT JOIN 更直观。

`FULL JOIN`（全连接）返回左右两表的所有行，匹配不上的部分用 NULL 填充，相当于两表的"并集"。

> 前端类比：FULL JOIN 类似于合并两个 Map，取并集，缺失的 key 用 undefined 填充。相当于 `[...mapA.entries(), ...mapB.entries()].reduce(mergeByKey)`，两边都保留。

业务场景：查询"所有用户和所有订单"（即使某些用户没下单、某些订单找不到对应用户——通常外键约束会避免后者，但数据修复场景可能需要）。

注意：MySQL 不支持 `FULL JOIN` 语法，需要用 `LEFT JOIN UNION RIGHT JOIN` 模拟。

```sql
-- ==============================
-- MySQL 版本（用 UNION 模拟 FULL JOIN）
-- ==============================
SELECT
    u.id AS user_id, u.username,
    o.id AS order_id, o.status
FROM users u
LEFT JOIN orders o ON u.id = o.user_id

UNION

SELECT
    u.id AS user_id, u.username,
    o.id AS order_id, o.status
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id
ORDER BY user_id, order_id;
```

```sql
-- ==============================
-- PostgreSQL 版本（原生 FULL JOIN）
-- ==============================
SELECT
    u.id AS user_id, u.username,
    o.id AS order_id, o.status
FROM users u
FULL JOIN orders o ON u.id = o.user_id
ORDER BY user_id, order_id;
```

#### 5.1.4 CROSS JOIN 与自连接（Self Join）

**CROSS JOIN（交叉连接）**：返回两表的笛卡尔积。如果左表有 M 行、右表有 N 行，结果就是 M x N 行。慎用，数据量可能爆炸。

业务场景：生成"所有用户 x 所有商品"的推荐矩阵（常用于生成维度组合）。

```sql
-- MySQL / PostgreSQL 通用
SELECT u.username, p.name AS product_name
FROM users u
CROSS JOIN products p;
-- 结果 4 用户 x 5 商品 = 20 行
```

**自连接（Self Join）**：一张表和自己连接，常用于树形结构（如员工-上级、分类-父分类）、对比同表数据。需要给同一张表起不同的别名来区分角色。

业务场景：员工表 `employees(id, name, manager_id)`，查询"每个员工及其直接上级姓名"。

```sql
-- MySQL / PostgreSQL 通用
CREATE TABLE employees (
  id         INT PRIMARY KEY,
  name       VARCHAR(64),
  manager_id INT
);

INSERT INTO employees(id, name, manager_id) VALUES
  (1, 'CEO',    NULL),
  (2, 'CTO',    1),
  (3, 'CFO',    1),
  (4, '前端组长', 2),
  (5, '后端组长', 2);

SELECT e.id    AS emp_id,
       e.name  AS emp_name,
       m.name  AS manager_name
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id
ORDER BY e.id;
```

执行结果（示意）：

```
emp_id | emp_name  | manager_name
-------+-----------+--------------
  1    | CEO       | NULL
  2    | CTO       | CEO
  3    | CFO       | CEO
  4    | 前端组长  | CTO
  5    | 后端组长  | CTO
```

自连接的精髓在于"同表两次出场，扮演不同角色"——`employees e` 是员工视角，`employees m` 是上级视角，用 `e.manager_id = m.id` 把两个视角关联起来。前端做"扁平数组转树形结构"时也会用类似思路：用 id 在数组里查 parent。

#### 5.1.5 实战：多表关联查询的商品列表与用户订单

综合场景：查询"每个订单的完整明细（用户名、订单状态、商品名、数量、单价、小计、订单总金额）"。这里用四表 JOIN，并在 PostgreSQL 版本中演示窗口函数 `SUM(...) OVER (PARTITION BY ...)` 来计算订单总金额。

```sql
-- ==============================
-- MySQL 版本
-- ==============================
SELECT
    o.id                 AS order_id,
    u.username,
    o.status,
    o.created_at,
    p.name               AS product_name,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS subtotal
FROM orders o
JOIN users u             ON o.user_id    = u.id
JOIN order_items oi      ON oi.order_id  = o.id
JOIN products p          ON oi.product_id = p.id
ORDER BY o.id, p.name;
```

```sql
-- ==============================
-- PostgreSQL 版本（含窗口函数计算订单总金额）
-- ==============================
SELECT
    o.id                 AS order_id,
    u.username,
    o.status,
    o.created_at,
    p.name               AS product_name,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS subtotal,
    -- 窗口函数：每个订单的明细总额（不压缩行，每行都带这个值）
    SUM(oi.quantity * oi.unit_price)
        OVER (PARTITION BY o.id)        AS order_total
FROM orders o
JOIN users u             ON o.user_id    = u.id
JOIN order_items oi      ON oi.order_id  = o.id
JOIN products p          ON oi.product_id = p.id
ORDER BY o.id, p.name;
```

说明：MySQL 8.0+ 也支持窗口函数，但 5.7 及以下不支持。在 MySQL 5.7 中要算订单总额，需要用子查询或派生表先 group by 算出来再 join。窗口函数的详细用法见 5.4 节。

---

### 5.2 子查询

子查询（Subquery）是嵌套在另一个查询中的 SELECT 语句，用小括号包裹。根据返回结果的结构，子查询分为：标量子查询、列子查询、行子查询、表子查询。

> 前端类比：子查询类似于 JavaScript 中的"函数嵌套调用"或 Promise 链。比如先 `getUserIds()` 返回一个 id 数组，再 `getOrdersByUserIds(ids)`。子查询就是"先查一批数据，再基于这批数据做下一步查询"。相关子查询则像 `Array.filter` 中依赖外部变量的回调——内层查询依赖外层每行的当前值。

#### 5.2.1 标量子查询

标量子查询返回"单行单列"（一个值），可以放在 SELECT、WHERE、HAVING 中，用于比较或作为计算字段。

业务场景：查询"每个商品的价格以及所有商品的平均价格"。

```sql
-- MySQL / PostgreSQL 通用
SELECT
    id, name, price,
    (SELECT AVG(price) FROM products) AS avg_price,
    price - (SELECT AVG(price) FROM products) AS diff_from_avg
FROM products
ORDER BY id;
```

业务场景：查询"比平均价格贵的商品"。

```sql
-- MySQL / PostgreSQL 通用
SELECT id, name, price
FROM products
WHERE price > (SELECT AVG(price) FROM products)
ORDER BY price DESC;
```

标量子查询因为只返回一个值，可以安全地用在 `>`、`=`、`<` 等比较运算符右侧，也可以直接作为 SELECT 的一列。注意：如果子查询意外返回多行，会报错"Subquery returns more than 1 row"。

#### 5.2.2 列子查询

列子查询返回"单列多行"，通常配合 `IN`、`ANY`、`ALL` 使用。

业务场景：查询"下过单的用户"。

```sql
-- MySQL / PostgreSQL 通用
SELECT id, username
FROM users
WHERE id IN (SELECT user_id FROM orders);
```

这里 `IN` 等价于"存在于集合中"——子查询先取出所有下过单的 user_id，外层用 IN 过滤。前端类比就是 `users.filter(u => orderedUserIds.includes(u.id))`。

#### 5.2.3 行子查询

行子查询返回"单行多列"，用于行级比较 `(a, b) = (SELECT x, y ...)`。

业务场景：查询"与 iPhone 15 同分类且价格相同的商品"（同一分类下价格相同的可能不止一个）。

```sql
-- MySQL / PostgreSQL 通用
SELECT id, name, price, category
FROM products
WHERE (category, price) = (
    SELECT category, price FROM products WHERE name = 'iPhone 15'
)
AND name <> 'iPhone 15';
```

行子查询把多个列作为整体比较，相当于"这个 (category, price) 元组等于子查询返回的元组"。比拆成两个独立比较更简洁。

#### 5.2.4 表子查询（派生表）

表子查询返回多行多列，通常放在 FROM 子句中作为派生表（Derived Table），必须起别名。

业务场景：查询"每个用户的订单数和总消费金额"。

```sql
-- MySQL / PostgreSQL 通用
SELECT
    u.id, u.username,
    COALESCE(agg.order_count, 0)  AS order_count,
    COALESCE(agg.total_spent, 0)  AS total_spent
FROM users u
LEFT JOIN (
    -- 派生表：先按用户聚合订单
    SELECT
        o.user_id,
        COUNT(*)                       AS order_count,
        SUM(oi.quantity * oi.unit_price) AS total_spent
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.id
    GROUP BY o.user_id
) agg ON agg.user_id = u.id
ORDER BY agg.total_spent DESC NULLS LAST;
```

派生表的思想是"先算一张中间结果表，再 join"。`COALESCE` 函数把 NULL 转成 0，对应前端的 `value ?? 0`。`NULLS LAST` 让 NULL 排在最后（MySQL 8.0+ 原生支持，PostgreSQL 也支持；MySQL 5.7 需用 `ORDER BY (total_spent IS NULL), total_spent DESC` 模拟）。

#### 5.2.5 相关子查询 vs 非相关子查询

**非相关子查询**：内层查询不依赖外层查询，只执行一次，结果供外层使用。前面的例子都是非相关子查询。

**相关子查询（Correlated Subquery）**：内层查询引用了外层查询的列，外层每扫描一行，内层就重新执行一次。性能通常较差（类似嵌套循环），但表达力强。

业务场景：查询"每个用户最新的一笔订单"（相关子查询写法）。

```sql
-- MySQL / PostgreSQL 通用
SELECT u.id, u.username, o.id AS order_id, o.created_at
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE o.created_at = (
    -- 相关子查询：依赖外层的 u.id
    SELECT MAX(o2.created_at)
    FROM orders o2
    WHERE o2.user_id = u.id
)
ORDER BY u.id;
```

提示：相关子查询虽然直观，但在大数据量下性能不佳。5.4 节的窗口函数能更高效地解决这类问题。用窗口函数改写：`ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC)` 取 rn=1 的行即可。

#### 5.2.6 EXISTS / IN / ANY / ALL 的用法与性能

**EXISTS**：判断子查询是否返回行，返回布尔值。相关子查询常配合 EXISTS 使用。EXISTS 一旦找到匹配就短路返回 true，效率高。

业务场景：查询"下过单的用户"（EXISTS 版）。

```sql
-- MySQL / PostgreSQL 通用
SELECT id, username
FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);
```

**IN vs EXISTS 性能经验**：当子查询结果集小、外层表大时，IN 性能更好；当外层表小、子查询结果集大时，EXISTS 更优。本质上都是"小表驱动大表"。现代优化器大多能自动改写两者，但理解原理有助于写高效的 SQL。

**ANY / ALL**：配合比较运算符使用。
- `x > ANY (子查询)`：x 大于子查询结果中的"任意一个"（即大于最小值）
- `x > ALL (子查询)`：x 大于子查询结果中的"所有"（即大于最大值）

业务场景：查询"价格比所有 phone 分类的商品都贵的商品"。

```sql
-- MySQL / PostgreSQL 通用
SELECT id, name, price
FROM products
WHERE price > ALL (
    SELECT price FROM products WHERE category = 'phone'
)
ORDER BY price DESC;
```

等价写法（更直观）：

```sql
SELECT id, name, price
FROM products
WHERE price > (SELECT MAX(price) FROM products WHERE category = 'phone')
ORDER BY price DESC;
```

> 前端类比：`> ANY` 类似 `x > Math.min(...arr)`，`> ALL` 类似 `x > Math.max(...arr)`。

---

### 5.3 聚合与分组

聚合操作是报表统计的核心。`GROUP BY` 按维度分组，聚合函数对每组计算汇总值。

> 前端类比：聚合分组就像前端状态管理里的"按字段分组聚合"，比如把订单列表按 `userId` 分组后求每组的 `amount` 总和。SQL 的 `GROUP BY` + `SUM()` 就是把这个工作下推到数据库完成，而不是把全量数据拉到应用层再用 `reduce` 算——前者省网络、省应用内存，后者把计算压力全压到前端进程。

#### 5.3.1 GROUP BY 与 HAVING

`GROUP BY` 按指定列分组，`SELECT` 中的非聚合列必须出现在 `GROUP BY` 中（MySQL 在 `ONLY_FULL_GROUP_BY` 模式下强制此规则，PostgreSQL 默认强制）。`HAVING` 用于对分组后的结果过滤，相当于"分组后的 WHERE"。

业务场景：查询"每个分类的商品数、平均价、最高价、最低价"。

```sql
-- MySQL / PostgreSQL 通用
SELECT
    category,
    COUNT(*)   AS product_count,
    AVG(price) AS avg_price,
    MAX(price) AS max_price,
    MIN(price) AS min_price
FROM products
WHERE stock > 0          -- WHERE 在分组前过滤行
GROUP BY category
HAVING COUNT(*) >= 1    -- HAVING 在分组后过滤组
ORDER BY product_count DESC;
```

**WHERE 与 HAVING 的区别**：
- WHERE：作用于"行"，在分组前过滤，不能用聚合函数。
- HAVING：作用于"组"，在分组后过滤，可以用聚合函数。

SQL 执行顺序：`FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT`。理解这个顺序很重要——SELECT 里起的别名在 HAVING 里不能直接用（因为 HAVING 先执行），但 MySQL 有个"扩展"允许 HAVING 用 SELECT 别名，PostgreSQL 不允许。

#### 5.3.2 聚合函数：COUNT / SUM / AVG / MIN / MAX

- `COUNT(*)`：统计行数（含 NULL 行）。
- `COUNT(col)`：统计 col 非空的行数（NULL 不计）。
- `COUNT(DISTINCT col)`：统计 col 去重后的非空值数量。
- `SUM/AVG`：只对非 NULL 值求和/求平均。AVG = SUM / COUNT(非NULL)。
- `MIN/MAX`：忽略 NULL。

业务场景：销售报表——"每个订单的总金额、商品件数、明细行数"。

```sql
-- MySQL / PostgreSQL 通用
SELECT
    o.id AS order_id,
    SUM(oi.quantity * oi.unit_price) AS total_amount,
    SUM(oi.quantity)                 AS total_qty,
    COUNT(*)                         AS line_count
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
GROUP BY o.id
ORDER BY total_amount DESC;
```

注意 COUNT 的坑：`COUNT(*)` 统计所有行，`COUNT(col)` 跳过 NULL。如果你 LEFT JOIN 后想统计"有明细的订单数"，用 `COUNT(oi.id)` 比 `COUNT(*)` 更准确——后者会把 LEFT JOIN 产生的全 NULL 行也算进去。

#### 5.3.3 GROUP_CONCAT（MySQL）/ STRING_AGG（PostgreSQL）

把分组内的多行字符串拼接成一个字符串，常用于"把一组标签拼成逗号分隔串"。

业务场景：查询"每个订单包含的商品名列表（逗号分隔）"。

```sql
-- ==============================
-- MySQL 版本
-- ==============================
SELECT
    o.id AS order_id,
    GROUP_CONCAT(p.name ORDER BY p.id SEPARATOR ', ') AS product_names
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN products p     ON p.id = oi.product_id
GROUP BY o.id;
-- 结果示例：1 | iPhone 15, AirPods Pro
```

```sql
-- ==============================
-- PostgreSQL 版本
-- ==============================
SELECT
    o.id AS order_id,
    STRING_AGG(p.name, ', ' ORDER BY p.id) AS product_names
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN products p     ON p.id = oi.product_id
GROUP BY o.id;
```

MySQL 的 `GROUP_CONCAT` 默认有长度限制（`group_concat_max_len`，默认 1024 字节），拼接长串前需 `SET SESSION group_concat_max_len = 102400;`。PostgreSQL 的 `STRING_AGG` 没有这种限制。

#### 5.3.4 实战：销售报表统计

综合场景：生成"按月统计的销售报表"——每月订单数、总销售额、客单价。

```sql
-- ==============================
-- MySQL 版本（按月统计）
-- ==============================
SELECT
    DATE_FORMAT(o.created_at, '%Y-%m')   AS month,
    COUNT(DISTINCT o.id)                  AS order_count,
    SUM(oi.quantity * oi.unit_price)      AS total_revenue,
    ROUND(AVG(oi.quantity * oi.unit_price), 2) AS avg_line_value
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
WHERE o.status = 'PAID'
GROUP BY DATE_FORMAT(o.created_at, '%Y-%m')
ORDER BY month DESC;
```

```sql
-- ==============================
-- PostgreSQL 版本（按月统计）
-- ==============================
SELECT
    TO_CHAR(o.created_at, 'YYYY-MM')      AS month,
    COUNT(DISTINCT o.id)                  AS order_count,
    SUM(oi.quantity * oi.unit_price)      AS total_revenue,
    ROUND(AVG(oi.quantity * oi.unit_price), 2) AS avg_line_value
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
WHERE o.status = 'PAID'
GROUP BY TO_CHAR(o.created_at, 'YYYY-MM')
ORDER BY month DESC;
```

注意 MySQL 用 `DATE_FORMAT` + `%Y-%m`，PostgreSQL 用 `TO_CHAR` + `YYYY-MM`，格式占位符完全不同，这是两库最易踩的坑之一。`ROUND` 在 PG 中要求数值类型，`AVG` 返回 NUMERIC，可以直接 ROUND。

#### 5.3.5 ROLLUP / CUBE / GROUPING SETS（多维聚合）

在分组统计中，经常需要"小计"和"总计"。MySQL 和 PostgreSQL 都支持 `ROLLUP` / `CUBE` / `GROUPING SETS`，但语法细节略有差异。

- ROLLUP：按维度层次产生小计和总计（从右向左逐层汇总）。
- CUBE：对所有维度组合产生小计。
- GROUPING SETS：自定义需要哪些分组组合。

业务场景：按"分类 + 是否有库存"二维统计商品数，并给出分类小计和总计。

```sql
-- ==============================
-- MySQL 版本（WITH ROLLUP）
-- ==============================
SELECT
    COALESCE(category, 'ALL')  AS category,
    COALESCE(
        CASE WHEN stock > 0 THEN 'Y' ELSE 'N' END,
        'ALL'
    )                            AS in_stock,
    COUNT(*)                     AS cnt
FROM products
GROUP BY category,
         CASE WHEN stock > 0 THEN 'Y' ELSE 'N' END
WITH ROLLUP;
```

```sql
-- ==============================
-- PostgreSQL 版本（GROUPING SETS，更灵活）
-- ==============================
SELECT
    COALESCE(category, 'ALL')  AS category,
    COALESCE(
        CASE WHEN stock > 0 THEN 'Y' ELSE 'N' END,
        'ALL'
    )                            AS in_stock,
    COUNT(*)                     AS cnt
FROM products
GROUP BY GROUPING SETS (
    (category, in_stock_expr),   -- 每个组合
    (category),                  -- 每个分类的小计
    ()                           -- 总计
)
-- 注意：PG 不允许在 GROUPING SETS 里直接引用 SELECT 别名或 CASE 表达式
-- 实际写法需用子查询先算出 in_stock 列：
```

PostgreSQL 的 `GROUPING SETS` 不能直接引用 SELECT 中的 CASE 别名，需要用子查询预处理。完整 PG 写法：

```sql
-- PostgreSQL 完整版（子查询预处理维度列）
WITH base AS (
    SELECT category,
           CASE WHEN stock > 0 THEN 'Y' ELSE 'N' END AS in_stock
    FROM products
)
SELECT
    COALESCE(category, 'ALL')  AS category,
    COALESCE(in_stock, 'ALL')  AS in_stock,
    COUNT(*)                   AS cnt
FROM base
GROUP BY GROUPING SETS (
    (category, in_stock),
    (category),
    ()
)
ORDER BY category NULLS LAST, in_stock NULLS LAST;
```

`GROUPING(col)` 函数能识别当前行是否是某维度的"汇总行"（是汇总返回 1，否则 0），用于区分"真实的 ALL 值"和"ROLLUP 产生的 NULL 小计"。

---

### 5.4 窗口函数（Window Functions）

窗口函数是 SQL 进阶的"分水岭"。它在不减少行数的前提下，对一组相关行（窗口）进行计算。窗口函数的输出行数等于输入行数，这与 `GROUP BY` 不同（GROUP BY 会把多行压缩成一行）。

> 前端类比：窗口函数类似于 JavaScript 的 `map` 而非 `reduce`。`reduce` 会把数组聚合成一个值（对应 GROUP BY），而 `map` 保留每个元素并对每个元素基于其"上下文"做计算（对应窗口函数）。比如对每个订单计算"它在同用户订单中的排名"——输入 N 行，输出还是 N 行，但多了排名列。

MySQL 8.0+ 和 PostgreSQL 都支持窗口函数。基本语法：

```sql
函数名(...) OVER (
    [PARTITION BY ...]   -- 分区，类似 GROUP BY 但不压缩行
    [ORDER BY ...]       -- 排序
    [frame 子句]         -- 窗口范围
)
```

#### 5.4.1 ROW_NUMBER / RANK / DENSE_RANK

这三个排序函数最常用：
- `ROW_NUMBER()`：唯一递增序号（1,2,3,4...），即使值相同也不重复。
- `RANK()`：相同值排名相同，但会跳过后续名次（1,2,2,4）。
- `DENSE_RANK()`：相同值排名相同，不跳过名次（1,2,2,3）。

业务场景：给商品按价格降序排名。

```sql
-- MySQL / PostgreSQL 通用
SELECT
    name, price, category,
    ROW_NUMBER() OVER (ORDER BY price DESC) AS rn,
    RANK()       OVER (ORDER BY price DESC) AS rank_no,
    DENSE_RANK() OVER (ORDER BY price DESC) AS dense_rank_no
FROM products
ORDER BY price DESC;
```

三者区别：假设有 3 个商品价格分别是 14999、14999、7999。ROW_NUMBER 给 1,2,3；RANK 给 1,1,4；DENSE_RANK 给 1,1,2。选哪个看业务：要"严格唯一序号"用 ROW_NUMBER，要"并列后跳名次"用 RANK（奥运金牌榜常用），要"并列不跳"用 DENSE_RANK。

#### 5.4.2 排行榜实战

业务场景：每个分类下价格最贵的 3 个商品（分区排名 + 过滤）。这是窗口函数最经典的用法——"分组取 TopN"。

```sql
-- MySQL / PostgreSQL 通用（CTE + 窗口函数）
WITH ranked AS (
    SELECT
        name, price, category,
        ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC) AS rn
    FROM products
)
SELECT name, price, category, rn
FROM ranked
WHERE rn <= 3
ORDER BY category, rn;
```

思路：先用 CTE 给每个分类内的商品按价格降序编号（PARTITION BY category 实现分区），再外层过滤 rn <= 3。在窗口函数出现前，这种"分组取 TopN"要用相关子查询或自连接实现，又慢又难写。窗口函数让这类需求变得优雅。

#### 5.4.3 LAG / LEAD

`LAG(col, n)` 取当前行前第 n 行的值；`LEAD(col, n)` 取当前行后第 n 行的值。常用于计算环比、同比、连续登录等时间序列场景。

业务场景：假设有日销售表 `daily_sales(sale_date, revenue)`，计算每天与前一天的环比增长率。

```sql
-- 先造数据（MySQL / PostgreSQL 通用）
CREATE TABLE daily_sales (sale_date DATE, revenue NUMERIC(10,2));
INSERT INTO daily_sales VALUES
  ('2024-01-01', 1000.00),
  ('2024-01-02', 1500.00),
  ('2024-01-03', 1200.00);
```

```sql
-- MySQL / PostgreSQL 通用
WITH daily AS (
    SELECT
        sale_date,
        revenue,
        LAG(revenue, 1) OVER (ORDER BY sale_date) AS prev_revenue
    FROM daily_sales
)
SELECT
    sale_date,
    revenue,
    prev_revenue,
    CASE WHEN prev_revenue IS NOT NULL AND prev_revenue <> 0
         THEN ROUND((revenue - prev_revenue) / prev_revenue * 100, 2)
         ELSE NULL
    END AS growth_pct
FROM daily
ORDER BY sale_date;
```

LAG 的第二个参数是偏移量（默认 1），第三个参数是默认值（当取不到时返回，默认 NULL）。LEAD 是 LAG 的"向后看"版本，用法对称。

#### 5.4.4 连续登录天数

业务场景：有用户登录日志 `login_log(user_id, login_date)`，计算每个用户的"最大连续登录天数"。这是面试高频题，也是窗口函数的经典应用。

核心思路：用 `ROW_NUMBER()` 给每个用户的登录日期按时间排序生成序号 rn，然后用 `login_date - rn` 作为分组键——连续的日期减去连续的序号会得到相同的日期（因为两个递增序列相减，差值恒定），相同 grp_key 的就是一段连续登录。

```sql
-- ==============================
-- MySQL 版本
-- ==============================
WITH base AS (
    SELECT
        user_id,
        login_date,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) AS rn
    FROM login_log
),
grp AS (
    SELECT
        user_id,
        login_date,
        rn,
        -- MySQL: 日期减去天数
        DATE_SUB(login_date, INTERVAL rn DAY) AS grp_key
    FROM base
)
SELECT
    user_id,
    MAX(consecutive_days) AS max_consecutive_days
FROM (
    SELECT user_id, grp_key, COUNT(*) AS consecutive_days
    FROM grp
    GROUP BY user_id, grp_key
) t
GROUP BY user_id
ORDER BY max_consecutive_days DESC;
```

```sql
-- ==============================
-- PostgreSQL 版本
-- ==============================
WITH base AS (
    SELECT
        user_id,
        login_date,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) AS rn
    FROM login_log
),
grp AS (
    SELECT
        user_id,
        login_date,
        rn,
        -- PostgreSQL: 日期可直接减整数（得到 DATE）
        login_date - rn AS grp_key
    FROM base
)
SELECT
    user_id,
    MAX(consecutive_days) AS max_consecutive_days
FROM (
    SELECT user_id, grp_key, COUNT(*) AS consecutive_days
    FROM grp
    GROUP BY user_id, grp_key
) t
GROUP BY user_id
ORDER BY max_consecutive_days DESC;
```

差异说明：MySQL 的 DATE 类型不能直接和整数相减，要用 `DATE_SUB(login_date, INTERVAL rn DAY)`；PostgreSQL 的 DATE 可以直接减整数（`login_date - rn` 返回 DATE）。这是两库日期运算的典型差异。

#### 5.4.5 SUM/AVG OVER PARTITION BY

聚合函数 + OVER 即变成窗口函数，对整个分区或滑动窗口聚合，但不压缩行。

业务场景：查询每个订单明细及其占该订单总额的百分比。

```sql
-- MySQL / PostgreSQL 通用
SELECT
    oi.order_id,
    p.name,
    oi.quantity * oi.unit_price AS line_total,
    SUM(oi.quantity * oi.unit_price) OVER (PARTITION BY oi.order_id) AS order_total,
    ROUND(
        oi.quantity * oi.unit_price /
        SUM(oi.quantity * oi.unit_price) OVER (PARTITION BY oi.order_id) * 100,
        2
    ) AS pct_of_order
FROM order_items oi
JOIN products p ON p.id = oi.product_id
ORDER BY oi.order_id, p.name;
```

这里 `SUM(...) OVER (PARTITION BY order_id)` 对每个订单算总额，但每行都保留——这正是窗口函数与 GROUP BY 的本质区别。

#### 5.4.6 窗口帧（Window Frame）

窗口帧定义了窗口函数的计算范围。默认行为：
- 有 ORDER BY 时：范围从分区第一行到当前行（`RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`）。
- 无 ORDER BY 时：整个分区。

可以自定义帧，例如"计算当前行及前 2 行、后 1 行的移动平均"。

```sql
-- MySQL / PostgreSQL 通用
SELECT
    sale_date, revenue,
    AVG(revenue) OVER (
        ORDER BY sale_date
        ROWS BETWEEN 2 PRECEDING AND 1 FOLLOWING
    ) AS moving_avg
FROM daily_sales
ORDER BY sale_date;
```

`ROWS BETWEEN 2 PRECEDING AND 1 FOLLOWING` 表示窗口包含"前 2 行 + 当前行 + 后 1 行"共 4 行（不足时按实际行数算）。RANGE 是按值范围界定，ROWS 是按行数界定，日常多用 ROWS。

#### 5.4.7 FIRST_VALUE / LAST_VALUE / NTH_VALUE

- `FIRST_VALUE`：取窗口第一行的值。
- `LAST_VALUE`：取窗口最后一行的值。注意默认帧是"到当前行"，所以 LAST_VALUE 默认取到当前行而非分区最后一行；想要"分区最后值"需显式指定 `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`。
- `NTH_VALUE`：取窗口第 n 行的值。

```sql
-- MySQL / PostgreSQL 通用
SELECT
    name, dept, score,
    FIRST_VALUE(name) OVER (PARTITION BY dept ORDER BY score DESC) AS dept_top_name,
    LAST_VALUE(name)  OVER (
        PARTITION BY dept ORDER BY score DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS dept_bottom_name
FROM employee_perf;
```

LAST_VALUE 的"默认帧陷阱"是窗口函数最常见的坑——很多人以为 LAST_VALUE 取分区最后一行，其实默认只取到当前行。必须显式扩大帧范围才能拿到分区末值。

---

### 5.5 CTE（公共表表达式）

CTE（Common Table Expression）通过 `WITH` 子句定义临时结果集，类似"在查询中定义临时视图"。CTE 让复杂查询更易读、可分步调试，还能实现递归查询。

> 前端类比：CTE 类似于把一个复杂计算拆成多个 `const` 变量，每个变量有语义化命名。子查询嵌套写就像一堆内联函数调用，层层嵌套难以阅读；CTE 就是把这些中间步骤提取成命名变量，使逻辑清晰。就像你把 `arr.filter(x => x > 0).map(y => y * 2).reduce(sum)` 拆成 `positive = arr.filter(...)`、`doubled = positive.map(...)`、`total = doubled.reduce(...)` 一样。

#### 5.5.1 WITH 子句的基本用法

业务场景：查询"消费金额排名前 3 的用户"。

```sql
-- MySQL / PostgreSQL 通用
WITH user_spending AS (
    -- 第一步：计算每个用户的总消费
    SELECT
        o.user_id,
        SUM(oi.quantity * oi.unit_price) AS total_spent
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.id
    WHERE o.status = 'PAID'
    GROUP BY o.user_id
),
ranked AS (
    -- 第二步：按消费金额排名
    SELECT
        user_id,
        total_spent,
        RANK() OVER (ORDER BY total_spent DESC) AS spending_rank
    FROM user_spending
)
-- 第三步：取前3并关联用户名
SELECT u.username, r.total_spent, r.spending_rank
FROM ranked r
JOIN users u ON u.id = r.user_id
WHERE r.spending_rank <= 3
ORDER BY r.spending_rank;
```

多个 CTE 用逗号分隔，每个 CTE 可以引用前面的 CTE，形成管道式数据流——这种"分步计算 + 命名"的写法，可读性远胜嵌套子查询，也方便逐段调试（可以先单独跑某个 CTE 看中间结果）。

#### 5.5.2 递归 CTE：树形结构查询

递归 CTE 是处理树形/图状数据的利器，常用于分类树、组织架构、菜单树、评论树。

语法结构：

```sql
WITH RECURSIVE cte_name(col1, col2, ...) AS (
    -- 初始项（锚点）：查询递归的起始行
    SELECT ...
    UNION ALL
    -- 递归项：引用自身，每轮把上一轮的结果当作"上一层"
    SELECT ... FROM cte_name WHERE ...
)
SELECT * FROM cte_name;
```

业务场景：商品分类树 `categories(id, name, parent_id)`，查询某个分类及其所有子孙分类（向下遍历）。

```sql
-- 先建表造数据（MySQL / PostgreSQL 通用）
CREATE TABLE categories (
    id        INT PRIMARY KEY,
    name      VARCHAR(64),
    parent_id INT
);
INSERT INTO categories(id, name, parent_id) VALUES
  (1, '电子产品', NULL),
  (2, '手机',     1),
  (3, '电脑',     1),
  (4, '笔记本',   3),
  (5, '台式机',   3),
  (6, '智能手机', 2),
  (7, '功能机',   2);
```

```sql
-- ==============================
-- MySQL 版本（递归 CTE 向下遍历）
-- ==============================
WITH RECURSIVE category_tree AS (
    -- 锚点：从根节点"电子产品"开始
    SELECT id, name, parent_id, 0 AS depth,
           CAST(name AS CHAR(1000)) AS path
    FROM categories
    WHERE id = 1
    UNION ALL
    -- 递归项：找上一层的子节点
    SELECT
        c.id, c.name, c.parent_id,
        ct.depth + 1,
        CONCAT(ct.path, ' > ', c.name)
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT id, name, depth, path
FROM category_tree
ORDER BY depth, id;
```

```sql
-- ==============================
-- PostgreSQL 版本（递归 CTE 向下遍历）
-- ==============================
WITH RECURSIVE category_tree AS (
    -- 锚点：需显式声明 path 类型，避免递归中类型不一致
    SELECT id, name, parent_id, 0 AS depth,
           CAST(name AS VARCHAR(1000)) AS path
    FROM categories
    WHERE id = 1
    UNION ALL
    SELECT
        c.id, c.name, c.parent_id,
        ct.depth + 1,
        ct.path || ' > ' || c.name      -- PG 用 || 拼接
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT id, name, depth, path
FROM category_tree
ORDER BY depth, id;
```

执行结果（示意）：

```
id | name      | depth | path
---+-----------+-------+------------------------
 1 | 电子产品  |   0   | 电子产品
 2 | 手机      |   1   | 电子产品 > 手机
 3 | 电脑      |   1   | 电子产品 > 电脑
 4 | 笔记本    |   2   | 电子产品 > 电脑 > 笔记本
 5 | 台式机    |   2   | 电子产品 > 电脑 > 台式机
 6 | 智能手机  |   2   | 电子产品 > 手机 > 智能手机
 7 | 功能机    |   2   | 电子产品 > 手机 > 功能机
```

**向上遍历**（找某节点的所有祖先）只需把递归项的连接条件反过来：锚点改为子节点，递归项改为 `JOIN category_tree ct ON c.id = ct.parent_id`（从子节点往上找父节点）。

**递归 CTE 的执行过程**：锚点查询产生初始结果集 R0，递归项以 R0 为输入产生 R1，再以 R1 为输入产生 R2……直到某轮结果为空。最终输出 R0 UNION ALL R1 UNION ALL R2 ...。

**防死循环**：如果数据中存在循环引用（A 的父是 B，B 的父是 A），递归 CTE 会无限循环。防护手段：
- MySQL 有递归深度限制 `cte_max_depth`（默认 1000），超过报错。
- PostgreSQL 默认限制递归次数，可用 `SET` 调整；也可在递归项里用数组记录已访问节点去重，例如 `WHERE c.id <> ALL(ct.visited)`。

#### 5.5.3 CTE 与子查询的性能对比

性能层面，CTE 与派生表（FROM 中的子查询）在多数场景下性能接近。但有两点关键差异：

**1. 物化（Materialization）特性差异**

- **PostgreSQL**：在 PG 12 之前，CTE 是"优化栅栏"（optimization fence），即 CTE 会独立执行并物化结果，外层查询把它当临时表用——即使外层只取 1 行，CTE 也会全量执行。从 PostgreSQL 12 开始，如果 CTE 只被引用一次且不是递归的，优化器可以把谓词下推到 CTE 内部。PG 12+ 提供 `MATERIALIZED` / `NOT MATERIALIZED` 关键字手动控制。
- **MySQL**：MySQL 8.0 把 CTE 视为派生表，通常会进行谓词下推等优化，性能与等价的派生表写法接近。MySQL 不支持 MATERIALIZED 关键字。

**2. 多次引用同一逻辑**

- 如果同一段子查询逻辑在主查询中被多次引用，CTE 写法更清晰，且 PG 物化后只执行一次（但 MySQL 未必物化，可能展开多次）。
- 相关子查询（引用外层列）无法用 CTE 等价替换，因为 CTE 是非相关的。

**实践建议**：
- 优先用 CTE 提升可读性，复杂查询拆成多个 CTE 分步写、分步调试。
- 性能敏感场景，用 `EXPLAIN ANALYZE` 对比 CTE 与派生表的执行计划。
- PostgreSQL 12+ 可用 `NOT MATERIALIZED` 强制内联展开以避免不必要的物化开销。
- 递归 CTE 是树形/图状数据的首选，比应用层递归调用数据库更高效（一次查询搞定 vs N 次 round-trip）。
- MySQL 的递归 CTE 有深度限制，需注意死循环；PostgreSQL 用数组去重更安全。

---

### 5.6 MySQL 与 PostgreSQL 语法差异速查

对于从 Node.js 转后端 Python 的开发者，常会在 MySQL 和 PostgreSQL 之间切换，两者语法差异容易踩坑。本节汇总常见差异。

#### 5.6.1 字符串拼接、日期函数、分页语法、类型转换

| 功能 | MySQL | PostgreSQL |
|------|-------|------------|
| 字符串拼接 | `CONCAT(a, b)` | `a || b`（原生支持） |
| 字符串拼接（含 NULL） | `CONCAT_WS(sep, a, b)` 忽略 NULL | `CONCAT_WS(sep, a, b)`（9.1+） |
| 当前日期时间 | `NOW()` / `CURRENT_TIMESTAMP` | `NOW()` / `CURRENT_TIMESTAMP` |
| 当前日期 | `CURDATE()` | `CURRENT_DATE` |
| 日期格式化 | `DATE_FORMAT(d, '%Y-%m-%d')` | `TO_CHAR(d, 'YYYY-MM-DD')` |
| 字符串转日期 | `STR_TO_DATE('2024-01-01', '%Y-%m-%d')` | `TO_DATE('2024-01-01', 'YYYY-MM-DD')` |
| 日期加减 | `DATE_ADD(d, INTERVAL 1 DAY)` | `d + INTERVAL '1 day'` |
| 日期差（天数） | `DATEDIFF(d1, d2)` | `(d1 - d2)` 返回 INTERVAL |
| 日期提取 | `YEAR(d)` / `MONTH(d)` | `EXTRACT(YEAR FROM d)` / `DATE_PART('year', d)` |
| 分页 | `LIMIT 10 OFFSET 20` | `LIMIT 10 OFFSET 20`（相同） |
| 分页（偏移写法） | `LIMIT 20, 10`（offset, count） | 不支持此语法 |
| 类型转换 | `CAST(x AS type)` / `CONVERT(x, type)` | `CAST(x AS type)` / `x::type` |
| NULL 替换 | `IFNULL(a, b)` | `COALESCE(a, b)`（通用） |
| 布尔类型 | 无真正 BOOLEAN（用 TINYINT(1)） | 真正的 BOOLEAN 类型 |
| 自增主键 | `AUTO_INCREMENT` | `SERIAL` / `BIGSERIAL` / `GENERATED ALWAYS AS IDENTITY` |
| 返回插入的 ID | `LAST_INSERT_ID()` | `RETURNING id` |
| 条件表达式 | `IF(cond, a, b)` | `CASE WHEN cond THEN a ELSE b END`（无 IF 函数） |

**分页深分页问题**：`LIMIT 1000000, 10` 会扫描 100 万行再丢弃，性能极差。优化方案：记录上一页最后一条的 id，用 `WHERE id > last_id LIMIT 10`（游标分页 / keyset pagination）。

```sql
-- 游标分页（MySQL / PostgreSQL 通用）
SELECT id, name, created_at
FROM products
WHERE id > :last_id     -- 上一页最后一条记录的 id
ORDER BY id
LIMIT 10;
```

游标分页的复杂度从 O(offset) 降到 O(limit)，是深分页的标准优化。缺点是不能随机跳页（只能"上一页/下一页"），且需要排序字段唯一稳定。

#### 5.6.2 JSON 操作语法对比

PostgreSQL 对 JSON 的支持非常成熟，MySQL 8.0+ 也加入了 JSON 支持，但函数名和语法略有不同。对前端转后端的开发者来说，JSON 是非常熟悉的格式，数据库原生支持 JSON 能省去很多 ORM 映射。

| 功能 | MySQL | PostgreSQL |
|------|-------|------------|
| 类型 | `JSON` | `JSONB`（推荐，带索引）或 `JSON` |
| 提取（点路径） | `JSON_EXTRACT(j, '$.name')` 或 `j->'$.name'` | `j->'name'`（返回 JSON） |
| 提取文本 | `j->>'$.name'` | `j->>'name'` |
| 提取数组元素 | `j->'$[0]'` | `j->'0'` 或 `j->0` |
| 路径表达式 | `$.a.b[0].c` | `a, b, 0, c`（逗号分隔） |
| 创建 JSON | `JSON_OBJECT('k', v)` | `json_build_object('k', v)` |
| 创建数组 | `JSON_ARRAY(a, b, c)` | `json_build_array(a, b, c)` |
| 判断键是否存在 | `JSON_CONTAINS_PATH(j, 'one', '$.name')` | `j ? 'name'` |
| JSON 包含 | `JSON_CONTAINS(j, '{"k":1}')` | `j @> '{"k":1}'` |

业务场景：用户表有 `preferences` JSON 字段，存储主题、语言等设置。查询"使用深色主题的用户"。

```sql
-- ==============================
-- MySQL 版本
-- ==============================
SELECT id, username, preferences->>'$.theme' AS theme
FROM users
WHERE preferences->>'$.theme' = 'dark';
```

```sql
-- ==============================
-- PostgreSQL 版本
-- ==============================
SELECT id, username, preferences->>'theme' AS theme
FROM users
WHERE preferences @> '{"theme":"dark"}'::jsonb;
```

PostgreSQL 的 `JSONB` 类型支持 GIN 索引，能大幅加速 JSON 查询；MySQL 需要用虚拟列 + 索引实现类似效果：

```sql
-- PostgreSQL JSONB GIN 索引
CREATE INDEX idx_users_prefs ON users USING GIN (preferences jsonb_path_ops);

-- MySQL 虚拟列 + 索引（STORED 表示物化存储该列）
ALTER TABLE users
  ADD COLUMN theme VARCHAR(32)
    GENERATED ALWAYS AS (JSON_UNQUOTE(JSON_EXTRACT(preferences, '$.theme'))) STORED,
  ADD INDEX idx_theme (theme);
```

#### 5.6.3 正则表达式支持差异

| 功能 | MySQL | PostgreSQL |
|------|-------|------------|
| 是否匹配 | `expr REGEXP 'pattern'` 或 `expr RLIKE 'pattern'` | `expr ~ 'pattern'`（区分大小写） |
| 不匹配 | `expr NOT REGEXP 'pattern'` | `expr !~ 'pattern'` |
| 不区分大小写匹配 | `expr REGEXP '(?i)pattern'`（8.0+） | `expr ~* 'pattern'` |
| 提取匹配 | 无内置提取，需存储过程 | `SUBSTRING(expr FROM 'pattern')` 或 `regexp_matches()` |
| 替换 | `REGEXP_REPLACE(expr, 'pat', 'rep')`（8.0+） | `REGEXP_REPLACE(expr, 'pat', 'rep')` |
| 数组返回所有匹配 | 不支持 | `regexp_matches(expr, 'pat', 'g')` |

业务场景：校验邮箱格式。

```sql
-- MySQL
SELECT email FROM users
WHERE email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$';

-- PostgreSQL
SELECT email FROM users
WHERE email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';
```

注意：MySQL 的 REGEXP 在 SQL 字符串中反斜杠需要双重转义（`\\.` 在字符串中是单个 `\.`）。PostgreSQL 的正则不需要双重转义。在 Python 代码中写 SQL 字符串时，建议用原始字符串 `r'...'` 避免转义地狱——尤其 Windows 环境下 GBK 编码与反斜杠组合容易出问题。

---

## 第六章 事务与并发控制（后端核心思维）

对于前端开发者而言，"事务"是一个全新的概念。前端代码大多操作的是内存中的状态或调用 API，很少需要考虑"多个操作必须全部成功或全部失败"。但在后端，事务是保证数据一致性的基石。

> 前端类比：事务类似于前端的一次"表单提交"。用户填写表单包含多个字段（姓名、地址、支付方式），你希望"要么全部提交成功，要么一个都不提交"——不会出现姓名保存了但地址没保存的中间态。事务就是数据库层面的"全有或全无"保证。又比如 Promise.all：你用 `Promise.all([saveProfile(), saveAddress(), savePayment()])` 希望要么全部成功要么整体失败，但 Promise.all 在任一 reject 时短路，已执行的请求无法回滚；数据库事务能真正实现"已执行的也能回滚"。

### 6.1 事务基础

#### 6.1.1 事务的 ACID 特性详解

事务具有四个特性，简称 ACID：

- **A - Atomicity（原子性）**：事务中的操作要么全部执行，要么全部不执行，不存在中间态。像上文表单提交的例子，不会出现"姓名存了但地址没存"的情况。实现机制：Undo Log（回滚日志），失败时用 Undo Log 撤销已执行的操作。
- **C - Consistency（一致性）**：事务执行前后，数据库从一个合法状态变为另一个合法状态。一致性是约束层面的（外键、唯一约束、检查约束等），事务执行中可能短暂违反约束，但提交后必须满足。一致性依赖原子性、隔离性、持久性共同保证，外加应用层的业务规则。
- **I - Isolation（隔离性）**：多个事务并发执行时互不干扰，一个事务的中间结果对其他事务不可见（取决于隔离级别）。实现机制：锁 + MVCC。
- **D - Durability（持久性）**：事务一旦提交，对数据的修改就是永久的，即使系统崩溃也不丢失。实现机制：Redo Log（重做日志），提交时先写 Redo Log 并刷盘，崩溃恢复时重放 Redo Log。

> 前端类比：ACID 类似于 Redux 的 reducer 约束——Action 要么完整执行改变状态（原子性），状态转换必须合法（一致性），多个 Action 顺序执行互不干扰（隔离性），store 持久化后刷新页面也在（持久性）。区别是数据库的 ACID 在并发和崩溃恢复上要严格得多。

#### 6.1.2 事务的生命周期：BEGIN -> COMMIT / ROLLBACK

事务的生命周期从 `BEGIN`（或 `START TRANSACTION`）开始，到 `COMMIT`（提交）或 `ROLLBACK`（回滚）结束。

```sql
-- MySQL / PostgreSQL 通用
BEGIN;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;  -- alice 扣 100
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;  -- bob 加 100
COMMIT;   -- 提交：两个修改一起生效
-- 或 ROLLBACK; -- 回滚：两个修改都撤销
```

> 前端类比：事务的生命周期类似 git 的"暂存区"。`BEGIN` 相当于开始准备一组改动，`COMMIT` 相当于 `git commit`（改动正式生效），`ROLLBACK` 相当于 `git checkout .`（丢弃所有改动）。但数据库事务的改动在提交前对其他事务的可见性取决于隔离级别，而 git 暂存区对他人完全不可见。

#### 6.1.3 自动提交（Autocommit）模式

MySQL 和 PostgreSQL 默认都开启自动提交（autocommit）。在自动提交模式下，每条 SQL 语句都被自动包裹在一个隐式事务中并立即提交——一条语句就是一个事务。

开启显式事务的方式：
- MySQL：`START TRANSACTION;` 或 `BEGIN;`。开启后自动提交被隐式关闭，直到 `COMMIT/ROLLBACK`。
- PostgreSQL：`BEGIN;` 或 `START TRANSACTION;`。PG 的 autocommit 是客户端行为，显式 BEGIN 后进入事务块。

```sql
-- MySQL：查看和设置自动提交
SELECT @@autocommit;        -- 默认 1（开启）
SET autocommit = 0;         -- 关闭，之后所有语句都在一个事务中直到显式 COMMIT
-- 推荐用显式 BEGIN 而非关闭 autocommit，避免遗漏 COMMIT
```

```sql
-- PostgreSQL：autocommit 默认开启（客户端特性）
-- psql 中默认每条语句自动提交
-- 显式开启事务：
BEGIN;
    -- ...
COMMIT;
```

重要提示：在 Python 的数据库驱动（如 pymysql、psycopg2）中，autocommit 默认通常是关闭的——即驱动会自动开启事务，你需要显式 `commit()` 或 `rollback()`。如果忘记 commit 就关闭连接，修改会被回滚。这是 Python 后端新手最常见的"数据没存进去"原因。

```python
# Python pymysql 示例（autocommit 默认关闭）
import pymysql
conn = pymysql.connect(host='localhost', user='root', password='xxx', db='shop')
cur = conn.cursor()
cur.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
cur.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
conn.commit()   # 必须！否则关闭连接时自动回滚
cur.close()
conn.close()
```

#### 6.1.4 保存点（SAVEPOINT）：部分回滚

保存点允许在事务内部设置"书签"，出错时可以回滚到保存点而非整个事务，实现部分回滚。这在批量操作中很有用——某条失败时回滚到保存点继续处理其余的，而不必整个事务重来。

```sql
-- MySQL / PostgreSQL 通用
BEGIN;
    INSERT INTO orders(user_id, status) VALUES (1, 'PAID');
    SAVEPOINT sp1;
    -- 这条可能失败（比如 product_id 不存在触发外键约束）
    INSERT INTO order_items(order_id, product_id, quantity, unit_price)
        VALUES (100, 999, 1, 7999.00);
    -- 失败后回滚到保存点，保留前面的 orders 插入
    ROLLBACK TO SAVEPOINT sp1;
    -- 继续其他操作
    INSERT INTO orders(user_id, status) VALUES (2, 'PAID');
COMMIT;
```

> 前端类比：保存点类似于浏览器表单的"分步骤保存"或"暂存草稿"。你填到第 3 步发现错了，可以只清除第 3 步重填，而不必清空整个表单。又像 git 的 `git stash` 局部暂存——回退到某个点但保留之前的工作。

---

### 6.2 隔离级别

#### 6.2.1 四种隔离级别

SQL 标准定义了四种隔离级别，从低到高：
1. **Read Uncommitted（读未提交）**：最低级别，一个事务可以读到其他事务未提交的数据（脏读）。
2. **Read Committed（读已提交）**：只能读到其他事务已提交的数据，避免脏读。但同一事务内两次读同一行可能不同（不可重复读）。PostgreSQL 默认级别。
3. **Repeatable Read（可重复读）**：同一事务内多次读同一行结果一致，避免不可重复读。但可能出现幻读（范围查询行数变化）。MySQL 默认级别。
4. **Serializable（可串行化）**：最高级别，事务完全串行执行，避免所有并发问题，但性能最差。

查看并设置隔离级别：

```sql
-- ==============================
-- MySQL 版本
-- ==============================
-- 查看全局和会话隔离级别
SELECT @@global.transaction_isolation, @@session.transaction_isolation;

-- 设置会话隔离级别
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- 设置全局隔离级别
SET GLOBAL TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```

```sql
-- ==============================
-- PostgreSQL 版本
-- ==============================
-- 查看当前隔离级别
SHOW transaction_isolation;
-- 或
SELECT current_setting('transaction_isolation');

-- 设置当前会话隔离级别（必须在事务外设置）
SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- 或在事务内设置下一个事务的隔离级别
BEGIN;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- ...
COMMIT;
```

#### 6.2.2 脏读、不可重复读、幻读的概念与复现

这三种异常是理解隔离级别的关键。我们用两个并发的数据库会话（事务 A、事务 B）来复现。

**脏读（Dirty Read）**：事务 A 读到了事务 B **未提交**的修改，如果 B 回滚，A 读到的就是"脏"数据。

```
时刻 T1: 事务A 开启，查询 balance=1000
时刻 T2: 事务B 开启，UPDATE balance=500（未提交）
时刻 T3: 事务A 再次查询，读到 balance=500  <- 脏读！
时刻 T4: 事务B ROLLBACK，balance 恢复 1000
时刻 T5: 事务A 拿着 balance=500 做业务决策 -> 错误！
```

**不可重复读（Non-Repeatable Read）**：事务 A 两次读同一行，中间事务 B **提交**了修改，导致 A 两次读到不同值。

```
T1: 事务A 查询 balance=1000
T2: 事务B UPDATE balance=800 并 COMMIT
T3: 事务A 再次查询 balance=800  <- 不可重复读！
```

**幻读（Phantom Read）**：事务 A 两次执行同一个范围查询，中间事务 B **插入/删除**了符合条件的行，导致 A 第二次查询多出或少了一些行（"幻影行"）。与不可重复读的区别：不可重复读针对同一行的值变化，幻读针对范围查询的行数变化。

```
T1: 事务A 查询 category='phone' 的商品，得到 1 行
T2: 事务B INSERT 一条 category='phone' 的新商品并 COMMIT
T3: 事务A 再次查询，得到 2 行  <- 幻读！
```

> 前端类比：脏读像"看了别人还没保存的草稿"；不可重复读像"第一次看是 v1，第二次看变成 v2 了"；幻读像"第一次列表 1 条，第二次变 2 条，多了个幽灵"。

#### 6.2.3 MySQL 默认 Repeatable Read（Next-Key Lock 解决幻读）

MySQL InnoDB 默认隔离级别是 **Repeatable Read（可重复读）**。在此级别下：
- 不可重复读：通过 MVCC（快照读）或 Next-Key Lock（当前读）避免。
- 幻读：InnoDB 通过 Next-Key Lock（临键锁）在"当前读"场景下避免幻读。

**快照读 vs 当前读**：
- 快照读：普通的 SELECT，读的是 MVCC 快照。Repeatable Read 下，事务内第一次快照读时建立快照，后续读的都是同一个快照，所以"可重复"。
- 当前读：`SELECT ... FOR UPDATE`、`UPDATE`、`DELETE`、`INSERT` 等，读的是最新已提交版本，并加锁。当前读通过 Next-Key Lock 防幻读。

复现 MySQL Repeatable Read 下无幻读（当前读场景）：

```sql
-- 会话 A
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN;
SELECT * FROM products WHERE category='phone' FOR UPDATE;  -- 当前读，加 Next-Key Lock
-- 此时若会话 B 尝试 INSERT category='phone' 的新行 -> 阻塞，直到 A 提交或超时
-- 会话 A COMMIT 后，B 才能插入
```

#### 6.2.4 PostgreSQL 默认 Read Committed

PostgreSQL 默认隔离级别是 **Read Committed（读已提交）**。在此级别下，事务内每条 SELECT 都读到最新已提交的数据，所以"不可重复读"和"幻读"在 PG 中是可能发生的（每条语句一个新快照）。

但 PostgreSQL 提供了 **Serializable（可串行化）** 级别，并且其实现方式与 MySQL 不同——PG 的 Serializable 基于 **SSI（Serializable Snapshot Isolation，可串行化快照隔离）**，通过追踪事务间的读写依赖关系，在运行时检测冲突并回滚冲突事务，而非靠加锁。PG 的 Serializable 在高冲突场景下可能回滚较多事务，但不会像传统两阶段锁那样产生大量阻塞。

PG 中若想避免不可重复读，可以使用 Repeatable Read 级别（PG 也支持），它基于"事务级快照"——整个事务使用第一次查询时的快照，所以可重复读且无幻读（快照读场景）。但 PG 的 Repeatable Read 不允许进行序列化冲突下的更新（会报 `could not serialize access due to concurrent update` 错误）。

#### 6.2.5 两数据库隔离级别实现的底层差异

| 方面 | MySQL InnoDB | PostgreSQL |
|------|--------------|------------|
| 默认隔离级别 | Repeatable Read | Read Committed |
| 实现基础 | 锁 + MVCC（Undo Log + Read View） | MVCC（元组 xmin/xmax + 快照） |
| RR 下幻读 | 当前读用 Next-Key Lock 防幻读 | 快照读无幻读（整事务一个快照）；当前读（FOR UPDATE）仍有幻读可能 |
| Serializable 实现 | 两阶段锁（2PL） | SSI（可串行化快照隔离），基于冲突检测回滚 |
| 快照粒度 | RR 级别：事务级快照（首次读时建立） | RR 级别：事务级快照；RC 级别：语句级快照 |
| 脏读 | 所有级别都禁止脏读 | 所有级别都禁止脏读 |
| 防幻读严格程度 | 当前读严格防幻读（加锁） | 快照读防幻读（基于快照），当前读可能幻读 |

**关键差异总结**：
- MySQL 偏"锁"路线，Repeatable Read + Next-Key Lock 在当前读场景防幻读；MVCC 主要服务快照读。
- PostgreSQL 偏"快照"路线，RC 每语句一个快照（可能幻读），RR 整事务一个快照（快照读无幻读），Serializable 用 SSI 无锁检测冲突。
- 从前端思维理解：MySQL 像"悲观"（先加锁防患于未然），PostgreSQL 像"乐观"（先干，冲突了再回滚）。这呼应了 6.5 节的悲观锁/乐观锁思想。

---

### 6.3 锁机制

锁是实现隔离性的直接手段。理解锁的分类和加锁规律，是排查死锁、慢查询的基础。

#### 6.3.1 共享锁（S Lock）vs 排他锁（X Lock）

- **共享锁（S Lock，Shared Lock）**：多个事务可同时持有同一数据的共享锁，用于读操作。加了 S 锁后，其他事务仍可读但不能写。
- **排他锁（X Lock，Exclusive Lock）**：只有一个事务能持有排他锁，用于写操作。加了 X 锁后，其他事务既不能读（当前读）也不能写。

> 前端类比：共享锁像"只读模式"，多人可同时看但不能改；排他锁像"独占编辑模式"，一个人改时别人既不能改也不能看（当前读）。但注意 MVCC 的快照读不需要加锁，所以"别人不能看"只针对当前读。

加锁语句：

```sql
-- 共享锁（S Lock）
-- MySQL 5.7 语法
SELECT * FROM products WHERE id = 1 LOCK IN SHARE MODE;
-- MySQL 8.0+ / PostgreSQL 语法
SELECT * FROM products WHERE id = 1 FOR SHARE;

-- 排他锁（X Lock）-- MySQL / PostgreSQL 通用
SELECT * FROM products WHERE id = 1 FOR UPDATE;
```

#### 6.3.2 表锁 vs 行锁

- **表锁（Table Lock）**：锁整张表，粒度大、开销小、并发低。MyISAM 只支持表锁；InnoDB 也支持显式表锁，但默认用行锁。
- **行锁（Row Lock）**：锁单行，粒度小、开销大、并发高。InnoDB 默认行锁。

行锁是加在**索引**上的（这是 InnoDB 的关键设计）。如果查询没有命中索引，InnoDB 不得不逐行加锁，退化为表锁（开销巨大）。所以：**行锁生效的前提是查询走索引**。

```sql
-- 走主键索引，加行锁
SELECT * FROM products WHERE id = 1 FOR UPDATE;   -- 锁 id=1 这一行

-- 若 category 无索引，InnoDB 逐行加锁，退化为表锁
SELECT * FROM products WHERE category = 'phone' FOR UPDATE;
-- 若 category 有索引，则只锁命中行
```

这条规则对后端开发极其重要——WHERE 条件是否走索引，直接决定 FOR UPDATE 是行锁还是表锁。在生产环境，给所有可能用于 FOR UPDATE 的列建索引是基本素养。

#### 6.3.3 意向锁、间隙锁（Gap Lock）、临键锁（Next-Key Lock）

**意向锁（Intention Lock）**：表级锁，用于表明事务"打算"在某行上加 S 或 X 锁，目的是让"表锁与行锁的兼容判断"高效。意向锁之间互不冲突（都是"意向"），但它使得加表锁时能快速判断是否有行锁冲突，而不必逐行检查。

- 意向共享锁（IS）：事务打算在某些行加 S 锁前，先在表上加 IS。
- 意向排他锁（IX）：事务打算在某些行加 X 锁前，先在表上加 IX。

**间隙锁（Gap Lock）**：锁住索引记录之间的"间隙"（不含记录本身），防止其他事务在间隙中插入新行。主要用于 Repeatable Read 下防幻读。间隙锁之间是兼容的（多个事务可以同时持有同一间隙的 Gap Lock，目的是共同阻止插入）。

**临键锁（Next-Key Lock）** = Record Lock（行锁）+ Gap Lock（间隙锁），锁住左开右闭区间 `(a, b]`。InnoDB Repeatable Read 的当前读默认用 Next-Key Lock。

举例：表中有 id=10, 20, 30 三行。Next-Key Lock 可能锁住 `(-inf, 10], (10, 20], (20, 30], (30, +inf]` 四个区间。事务 A 在 `WHERE id BETWEEN 15 AND 25 FOR UPDATE` 时会锁住 `(10, 20]` 和 `(20, 30]`，阻止其他事务在 11~30 之间插入新行。

#### 6.3.4 死锁的产生与排查

死锁：两个或多个事务互相持有对方需要的锁，导致循环等待。数据库有死锁检测机制，会主动牺牲（回滚）一个事务来打破死锁。

经典死锁场景（两个事务以相反顺序加锁）：

```
时刻 T1: 事务A: UPDATE accounts SET balance=balance-100 WHERE id=1;  -- 锁住 id=1
时刻 T2: 事务B: UPDATE accounts SET balance=balance-100 WHERE id=2;  -- 锁住 id=2
时刻 T3: 事务A: UPDATE accounts SET balance=balance+100 WHERE id=2; -- 等 id=2 的锁
时刻 T4: 事务B: UPDATE accounts SET balance=balance+100 WHERE id=1; -- 等 id=1 的锁 -> 死锁!
```

**排查死锁（MySQL）**：

```sql
-- 查看最近一次死锁信息
SHOW ENGINE INNODB STATUS\G
-- 输出中的 "LATEST DETECTED DEADLOCK" 部分会显示死锁时两个事务执行的 SQL 和锁信息

-- 开启死锁日志（排查用，生产环境慎用，日志量大）
SET GLOBAL innodb_print_all_deadlocks = ON;
-- 死锁信息会写入 error log
```

**排查死锁（PostgreSQL）**：
- PG 默认会自动检测死锁并回滚一个事务，错误信息为 `deadlock detected`。
- 日志中查看详细死锁信息。
- `pg_locks` 视图查看当前锁等待情况。

```sql
-- PostgreSQL 查看锁等待
SELECT
    pid, locktype, relation::regclass, mode, granted,
    query
FROM pg_locks
JOIN pg_stat_activity USING (pid)
WHERE NOT granted;
```

#### 6.3.5 死锁的预防策略

1. **固定加锁顺序**：所有事务按相同顺序加锁（如按 id 升序）。这是最有效的预防手段——上面死锁示例中，如果 A、B 都先锁 id=1 再锁 id=2，就不会死锁。
2. **缩短事务**：事务越长，持锁时间越久，冲突概率越高。把非数据库操作（如调用外部 API）移出事务。
3. **降低隔离级别**：隔离级别越低，加锁越少，冲突越少，但需评估一致性风险。
4. **使用合适的索引**：避免行锁退化为表锁（见 6.3.2）。
5. **大事务拆小**：大批量更新拆成小批次，每批提交，缩短持锁时间。
6. **乐观锁替代悲观锁**：低冲突场景用乐观锁减少加锁（见 6.5 节）。

> 前端类比：死锁类似两个人互相谦让让对方先过门，结果两人都卡住。预防死锁就像约定"都靠右行"，固定方向就不会对撞。

---

### 6.4 MVCC（多版本并发控制）

MVCC（Multi-Version Concurrency Control，多版本并发控制）是现代数据库实现读写不互相阻塞的核心技术。理解 MVCC 能解释很多"奇怪"的并发现象。

#### 6.4.1 MVCC 的核心思想：读写不互相阻塞

在没有 MVCC 的数据库中，读操作要加共享锁，写操作要加排他锁，读写互相阻塞——写事务进行时其他事务不能读，读事务进行时其他事务不能写。这在高并发场景下不可接受。

MVCC 的核心思想是：为数据维护多个版本，读操作读取一个合适的"历史快照"，写操作创建新版本，两者操作不同版本，互不阻塞。

> 前端类比：MVCC 类似于前端的"不可变数据"（immutable data）思想。就像 Redux 的 reducer，每次修改不直接改原状态，而是返回一个新版本；读取时用特定时刻的快照。多个"读者"看不同时间点的快照，互不影响，而"写者"在创建新版本。Immutable.js 的结构共享也与 MVCC 的版本链有异曲同工之妙。

#### 6.4.2 MySQL InnoDB 的 MVCC 实现：Undo Log + Read View

MySQL InnoDB 的 MVCC 依赖两个组件：**Undo Log（回滚日志）**和 **Read View（读视图）**。

**Undo Log（版本链）**：每行数据除了当前值，在 Undo Log 中保存了历史版本。每次 UPDATE 时，旧值被写入 Undo Log，行记录中有 `roll_pointer`（回滚指针）指向 Undo Log 中的旧版本，形成版本链。这样从当前版本顺着 roll_pointer 可以回溯所有历史版本。

**Read View（读视图）**：事务执行快照读时，会生成一个 Read View，记录当时所有"活跃事务"（未提交）的 ID 列表。读取某行时，顺着版本链找到对该事务"可见"的版本。可见性判断规则：
- 若版本的 trx_id == 当前事务 id（自己改的），可见。
- 若版本的 trx_id < Read View 中最小活跃事务 id（版本在 Read View 创建前已提交），可见。
- 若版本的 trx_id >= Read View 中最大事务 id+1（版本在 Read View 创建后才产生），不可见。
- 若版本的 trx_id 在活跃事务列表中（未提交），不可见，顺版本链往前找。

**Read Committed vs Repeatable Read 在 MVCC 上的差异**：
- Read Committed：每条 SELECT 都生成新的 Read View -> 能读到最新已提交。
- Repeatable Read：事务内第一次快照读生成 Read View，后续复用 -> 读到的始终是首次快照，所以"可重复"。

#### 6.4.3 PostgreSQL 的 MVCC 实现：元组头部 xmin/xmax + 旧版本存储

PostgreSQL 的 MVCC 与 MySQL 有本质不同。PG 在每行数据（元组）的头部记录 `xmin` 和 `xmax` 字段：

- **xmin**：插入该版本的事务 ID。
- **xmax**：删除该版本的事务 ID（0 表示未删除）。
- UPDATE 在 PG 中是"先标记删除旧版本（设置 xmax）+ 插入新版本"，不是原地更新。

PG 通过快照（Snapshot）来判断哪个版本对当前事务可见。快照包含"活跃事务列表"概念，逻辑类似 MySQL 的 Read View。读取时，对每行的版本链，根据 xmin/xmax 和快照判断可见性。

PG 的旧版本不像 MySQL 那样存在 Undo Log，而是直接存在表的数据文件中（与当前版本混放），由 **VACUUM** 进程清理。这导致表可能膨胀（bloat），需要定期 VACUUM。

#### 6.4.4 两者 MVCC 实现的关键差异与性能影响

| 方面 | MySQL InnoDB | PostgreSQL |
|------|--------------|------------|
| 旧版本存储位置 | Undo Log（独立日志段） | 表数据文件中（与当前版本混放） |
| 旧版本清理 | Purge 线程自动清理 Undo Log | VACUUM 进程清理（需手动或 autovacuum） |
| 表膨胀问题 | Undo Log 占空间但表本身不膨胀 | 表和索引可能膨胀，需 VACUUM/autovacuum |
| 回滚 | Undo Log 天然支持，快 | 需用旧版本（xmax 标记），回滚后旧版本需清理 |
| 索引维护 | UPDATE 走原地更新，索引维护较高效 | UPDATE = DELETE+INSERT，索引更新开销大 |
| 回滚段空间 | 可配置 undo 表空间大小 | 无独立回滚段，旧版本占表空间 |

**性能影响总结**：
- MySQL 的 Undo Log 方案：优点是表本身不膨胀，回滚快；缺点是长事务会导致 Undo Log 膨胀，影响其他事务的版本链遍历性能。
- PostgreSQL 的多版本混放方案：优点是实现简单，回滚无需额外操作（旧版本还在）；缺点是表和索引会膨胀，需 VACUUM 维护，UPDATE 性能不如 MySQL（因为要维护索引的删除+插入）。这也是 PG 频繁 UPDATE 场景需要优化的原因。

> 前端类比理解差异：MySQL 的 MVCC 像"Git 的提交历史"——旧版本存在独立的 Undo Log（类似 git 的对象库），主表只存当前版本（类似工作区），清理 Undo Log 类似 git gc。PostgreSQL 的 MVCC 像"文件系统保留了多个副本"——新旧版本混在一个目录，用 xmin/xmax 标记死活，需要定期 VACUUM 清理（类似磁盘碎片整理）。Git 的对象库和磁盘副本是两种不同的多版本管理思路，各有利弊。

---

### 6.5 乐观锁与悲观锁

在并发更新同一行数据时（如扣库存、扣余额），如何保证正确性？主要有两种策略：悲观锁和乐观锁。

> 前端类比：悲观锁像"排队上厕所"——一个人进去时锁门，其他人必须在门外等。乐观锁像"共享文档协作"——大家都能编辑，但保存时发现版本已变旧就提示冲突、让你重新基于最新版编辑（类似 git pull --rebase 后合并）。

#### 6.5.1 悲观锁：SELECT ... FOR UPDATE

悲观锁假设"冲突一定会发生"，在读取数据时就加排他锁，阻塞其他事务的修改。

业务场景：扣减库存。事务先锁住商品行，再扣减，保证不会超卖。

```sql
-- ==============================
-- MySQL 版本（悲观锁扣库存）
-- ==============================
BEGIN;
-- 先锁住商品行（当前读 + 加 X 锁）
SELECT stock FROM products WHERE id = 1 FOR UPDATE;
-- 应用层判断 stock >= 购买数量
-- 扣减库存
UPDATE products SET stock = stock - 1 WHERE id = 1;
COMMIT;
```

PostgreSQL 语法相同（`FOR UPDATE`）。注意：在 PostgreSQL 的 Read Committed 下，`FOR UPDATE` 会等已持有锁的事务结束后，重新读最新值（而非阻塞时的快照值）。MySQL 的 FOR UPDATE 行为类似。

**悲观锁的问题**：高并发下，大量事务排队等锁，吞吐量低；还可能死锁。

#### 6.5.2 乐观锁：version 字段 + CAS 思想

乐观锁假设"冲突很少发生"，不加锁，更新时检查版本号是否变化，变化了说明被别人改过，重试或失败。

实现：表中加 `version` 字段，每次更新 version+1。更新语句的 WHERE 带上 version 条件。

先给 products 表加 version 字段：

```sql
-- MySQL
ALTER TABLE products ADD COLUMN version INT NOT NULL DEFAULT 0;
-- PostgreSQL
ALTER TABLE products ADD COLUMN version INT NOT NULL DEFAULT 0;
```

```sql
-- ==============================
-- MySQL / PostgreSQL 通用（乐观锁扣库存）
-- ==============================
-- 1. 先查询当前 stock 和 version（不加锁）
SELECT id, stock, version FROM products WHERE id = 1;
-- 假设读到 stock=10, version=3

-- 2. 应用层判断 stock >= 购买数量

-- 3. 更新时带上 version 条件（CAS：Compare And Swap）
UPDATE products
SET stock = stock - 1, version = version + 1
WHERE id = 1 AND version = 3;
-- 若返回 affected_rows = 1，成功；若 = 0，说明 version 已变，需重试
```

> 前端类比：乐观锁的 CAS 思想和前端表单的"脏检查"非常像。编辑表单时，你先读取数据（记录初始 version），提交时后端检查"你基于的版本是否还是当前版本"，如果不是说明被别人改过，提示"数据已被他人修改，请刷新重试"。这与 React/Angular 表单的 optimistic update + 冲突检测思路一致。

#### 6.5.3 适用场景对比

| 方面 | 悲观锁 | 乐观锁 |
|------|--------|--------|
| 适用场景 | 高冲突（写多读多） | 低冲突（写少冲突少） |
| 吞吐量（高冲突） | 优（避免重试开销） | 差（大量重试浪费 CPU） |
| 吞吐量（低冲突） | 差（不必要的加锁阻塞） | 优（几乎不阻塞） |
| 死锁风险 | 高（多个 FOR UPDATE 交叉） | 无（不加锁） |
| 实现复杂度 | 简单 | 中等（需重试逻辑） |
| 响应延迟 | 高（等锁） | 低（失败快，但重试有开销） |

#### 6.5.4 数据库锁的局限性：单机锁无法跨服务/跨节点

数据库锁只对"同一个数据库实例"内的并发有效。在微服务架构下，同一业务操作可能涉及多个服务、多个数据库实例，单机数据库锁无法协调跨服务的并发。这时需要分布式锁。

#### 6.5.5 分布式锁的引入：Redis SETNX / Redlock 算法（提及，详细在第九章）

当需要跨服务/跨节点互斥时，常用 Redis 实现分布式锁。基本原理：用 `SET key value NX PX timeout`（NX 表示不存在才设置，PX 设置过期，timeout 为毫秒）实现互斥。Redlock 算法是 Redis 作者提出的多节点版本来提升容错性。

分布式锁与数据库锁的配合模式：分布式锁用于"限流入口"（如限制同一商品同时只有 N 个请求进入库存扣减逻辑），数据库事务 + 行锁用于"数据层最后防线"。

```python
# 伪代码：Redis 分布式锁 + 数据库乐观锁的经典模式（Python FastAPI 场景）
import redis
import pymysql   # 或 psycopg2

def deduct_stock(product_id: int, qty: int):
    r = redis.Redis(host='localhost', port=6379)
    lock_key = f"lock:product:{product_id}"
    # 1. 获取分布式锁（防并发入口）
    if not r.set(lock_key, "1", nx=True, px=3000):
        raise Exception("系统繁忙，请稍后重试")
    try:
        # 2. 数据库事务内扣库存（数据层最后防线）
        with db.cursor() as cur:
            cur.execute("SELECT stock, version FROM products WHERE id=%s", (product_id,))
            stock, version = cur.fetchone()
            if stock < qty:
                raise Exception("库存不足")
            cur.execute(
                "UPDATE products SET stock=stock-%s, version=version+1 WHERE id=%s AND version=%s",
                (qty, product_id, version)
            )
            if cur.rowcount == 0:
                raise Exception("并发冲突，请重试")
        db.commit()
    finally:
        # 3. 释放分布式锁
        r.delete(lock_key)
```

#### 6.5.6 实战：秒杀场景的库存扣减方案对比

秒杀是典型的"超高并发写"场景，库存扣减方案的选择直接决定系统能否扛住流量。

**方案 A：纯数据库悲观锁**（简单但吞吐量有限）

```sql
-- MySQL / PostgreSQL
BEGIN;
SELECT stock FROM products WHERE id = 1 FOR UPDATE;
-- 判断后扣减
UPDATE products SET stock = stock - 1 WHERE id = 1;
COMMIT;
```
适用：并发量不高（数百 QPS）。优点是简单可靠；缺点是高并发下行锁竞争严重，吞吐量低。

**方案 B：纯数据库乐观锁**（中并发可接受）

```sql
UPDATE products SET stock = stock - 1, version = version + 1
WHERE id = 1 AND version = 3 AND stock >= 1;
-- affected_rows=1 成功，=0 失败重试
```
适用：并发量中等、冲突率不高。优点无锁等待；缺点是冲突率高时重试风暴浪费资源。

**方案 C：Redis 预扣库存 + 异步落库**（高并发主流方案）

思路：将库存预热到 Redis，请求来时用 Redis 原子扣减（Lua 脚本保证原子性），扣减成功则发消息异步落库，数据库层用乐观锁兜底。

```python
# 伪代码
LUA_SCRIPT = """
local stock = redis.call('GET', KEYS[1])
if not stock then return -1 end
if tonumber(stock) < tonumber(ARGV[1]) then return 0 end
return redis.call('DECRBY', KEYS[1], ARGV[1])
"""
# Redis 原子扣减
result = r.eval(LUA_SCRIPT, 1, f"stock:product:{pid}", qty)
if result == 0: raise Exception("库存不足")
# 发送 MQ 异步创建订单、扣减数据库库存
```
适用：超高并发秒杀。优点是 Redis 扛住读并发，数据库压力小；缺点是引入 Redis-MQ-DB 一致性复杂度。

> 小结：从前端视角看，悲观锁/乐观锁/分布式锁的演进，和前端从"同步阻塞"到"异步回调"到"事件驱动"的演进类似——都是根据并发量级选择合适的"协调机制"。低并发用简单的（悲观锁/同步），高并发用高性能的（Redis 异步预扣）。

---

### 6.6 事务实战场景

本节通过具体业务场景，把前面学的事务、锁、MVCC 知识综合运用。

#### 6.6.1 转账场景：余额扣减 + 记录流水的事务设计

转账是事务的"教科书"案例：A 向 B 转账 100 元，A 扣 100、B 加 100、记录一条流水，三者必须原子。

设计要点：
1. **固定加锁顺序**：按账户 id 升序加锁，避免死锁。
2. **余额不能为负**：扣减前检查余额。
3. **流水表**：记录每笔交易用于对账。

```sql
-- ==============================
-- MySQL 版本（建表 + 转账事务）
-- ==============================
CREATE TABLE accounts (
    id      BIGINT PRIMARY KEY,
    name    VARCHAR(64),
    balance DECIMAL(12,2) NOT NULL DEFAULT 0,
    version INT NOT NULL DEFAULT 0
);
CREATE TABLE transfer_log (
    id           BIGINT PRIMARY KEY AUTO_INCREMENT,
    from_id      BIGINT,
    to_id        BIGINT,
    amount       DECIMAL(12,2),
    created_at   DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3)
);

INSERT INTO accounts VALUES (1, 'alice', 1000, 0), (2, 'bob', 500, 0);
```

转账事务（悲观锁版，按 id 升序加锁防死锁）：

```sql
-- MySQL / PostgreSQL 通用
-- 假设从 id=2 向 id=1 转账 100（固定顺序：先锁小的 id）
BEGIN;
    -- 固定顺序：先锁 id 较小的，避免 A-B 与 B-A 反向加锁死锁
    SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;   -- 锁 id=1
    SELECT balance FROM accounts WHERE id = 2 FOR UPDATE;   -- 锁 id=2

    -- 检查转出方余额（id=2 转出，余额需 >= 100）
    -- 应用层读取后判断 balance >= 100

    UPDATE accounts SET balance = balance + 100 WHERE id = 1;  -- id=1 收
    UPDATE accounts SET balance = balance - 100 WHERE id = 2;  -- id=2 付

    INSERT INTO transfer_log(from_id, to_id, amount) VALUES (2, 1, 100);
COMMIT;
```

转账事务（乐观锁版，适合低冲突）：

```sql
-- MySQL / PostgreSQL 通用
-- 先在应用层读取两个账户的 version：v1, v2
BEGIN;
    UPDATE accounts SET balance = balance + 100, version = version + 1
    WHERE id = 1 AND version = :v1;
    -- affected_rows=1 才继续，否则回滚重试

    UPDATE accounts SET balance = balance - 100, version = version + 1
    WHERE id = 2 AND version = :v2 AND balance >= 100;
    -- affected_rows=1 才继续

    INSERT INTO transfer_log(from_id, to_id, amount) VALUES (2, 1, 100);
COMMIT;
```

#### 6.6.2 订单创建：扣库存 + 创建订单 + 生成支付单的原子性保障

电商下单涉及多个表操作：扣库存、创建订单、生成支付单、扣优惠券等，必须在一个事务内，保证不超卖、不留孤立数据。

```sql
-- ==============================
-- MySQL 版本（下单事务）
-- ==============================
-- 前置：假设购物车已校验好商品和数量
BEGIN;
    -- 1. 扣库存（悲观锁，防超卖）
    SELECT stock FROM products WHERE id = :pid FOR UPDATE;
    -- 应用层判断 stock >= qty
    UPDATE products SET stock = stock - :qty WHERE id = :pid;

    -- 2. 创建订单（状态为待支付）
    INSERT INTO orders(user_id, status) VALUES (:uid, 'PENDING_PAYMENT');
    SET @order_id = LAST_INSERT_ID();   -- MySQL 取刚插入的 id

    -- 3. 创建订单明细
    INSERT INTO order_items(order_id, product_id, quantity, unit_price)
    VALUES (@order_id, :pid, :qty, :price);

    -- 4. 生成支付单
    INSERT INTO payments(order_id, amount, status) VALUES (@order_id, :total, 'PENDING');
COMMIT;
```

```sql
-- ==============================
-- PostgreSQL 版本（下单事务，用 RETURNING 简化）
-- ==============================
BEGIN;
    -- 1. 扣库存（用 RETURNING + WHERE stock >= qty 一步到位）
    UPDATE products
    SET stock = stock - :qty
    WHERE id = :pid AND stock >= :qty
    RETURNING stock;
    -- 若没返回行，说明库存不足或条件不满足，执行 ROLLBACK

    -- 2. 创建订单并取回 id，用 CTE 链式插入明细
    WITH new_order AS (
        INSERT INTO orders(user_id, status) VALUES (:uid, 'PENDING_PAYMENT')
        RETURNING id
    )
    INSERT INTO order_items(order_id, product_id, quantity, unit_price)
    SELECT id, :pid, :qty, :price FROM new_order;

    -- 3. 生成支付单
    INSERT INTO payments(order_id, amount, status)
    SELECT id, :total, 'PENDING'
    FROM orders
    WHERE id = (SELECT id FROM new_order);
    -- 注：CTE 在同一语句外不可复用，这里改用 currval 取序列当前值
COMMIT;
```

> 说明：PostgreSQL 的 `RETURNING` 子句能直接返回插入/更新/删除的行，比 MySQL 的 `LAST_INSERT_ID()` 更灵活强大，可以在 CTE 中链式使用。MySQL 不支持 RETURNING，只能用 `LAST_INSERT_ID()`（仅单个连接内、且只返回同表 AUTO_INCREMENT 的值）。

#### 6.6.3 批量操作：大批量数据更新的事务控制

批量更新（如全表更新状态、批量插入）如果放在一个大事务里，会持有大量锁、产生大量 Undo Log、可能导致主从延迟。应拆分小批次。

错误做法（一个大事务）：

```sql
-- 错误：一个大事务更新 100 万行，锁多、久、易超时
BEGIN;
UPDATE huge_table SET status = 'PROCESSED' WHERE status = 'PENDING';
COMMIT;
```

正确做法（分批次，每批小事务）：

```sql
-- MySQL / PostgreSQL 通用
-- 每次更新 1000 行，分批提交
BEGIN;
    UPDATE huge_table SET status = 'PROCESSED'
    WHERE id IN (
        SELECT id FROM huge_table WHERE status = 'PENDING' LIMIT 1000
    );
COMMIT;
-- 循环执行直到没有 PENDING 行
```

对于批量插入，也建议分批次。MySQL 可用 `SET autocommit=0` 后批量 INSERT，每 1000 行 COMMIT 一次。

```sql
-- MySQL 批量插入
SET autocommit = 0;
INSERT INTO t(a,b) VALUES (1,2),(3,4),...;  -- 每 1000 行一批
COMMIT;
-- 再插入下一批
INSERT INTO t(a,b) VALUES (...);
COMMIT;
SET autocommit = 1;
```

```sql
-- PostgreSQL 批量插入（COPY 更快）
-- 大批量导入推荐用 COPY 命令
COPY target_table(col1, col2) FROM '/path/to/file.csv' WITH (FORMAT csv);
-- 或分批 INSERT
```

#### 6.6.4 分布式事务初探：两阶段提交（2PC）、Saga 模式、最终一致性

微服务架构下，一个业务操作可能跨多个数据库实例/消息队列，单机事务无法保证跨库一致性，需要分布式事务方案。

**两阶段提交（2PC，Two-Phase Commit）**：
- 阶段一（准备阶段）：协调者问所有参与者"能否提交"，参与者执行操作但不提交，预留资源，回复 yes/no。
- 阶段二（提交/中止阶段）：若所有参与者都 yes，协调者发 commit；任一 no 或超时，发 abort。
- 缺点：协调者单点、同步阻塞（参与者锁定资源等待）、性能差。XA 协议是 2PC 的标准实现，MySQL 支持 XA，但性能开销大，高并发场景少用。

> 前端类比：2PC 类似于"开会决议"。先问所有人"明天能否到场？"（准备阶段），所有人都说能，才正式开会（提交）；有人来不了就取消（中止）。问题是有人"准备了"但一直等不到最终通知，资源就被占用着。

**Saga 模式**：长事务拆成多个本地事务，每个本地事务有对应的"补偿事务"。任一步骤失败，反向执行已完成步骤的补偿事务，最终达到一致（不保证隔离性，但保证最终一致性）。

```
正常：T1(扣库存) -> T2(创建订单) -> T3(扣余额) -> T4(发通知)
失败：T3失败 -> C2(取消订单) -> C1(回滚库存)  -- 补偿事务反向执行
```

> 前端类比：Saga 像前端的"乐观更新 + 回滚 UI"。用户点赞时 UI 先变红（T1），再调 API；API 失败就把 UI 变回灰色（C1 补偿）。Saga 把这种思路搬到跨服务事务上。

**最终一致性（可靠消息最终一致性）**：本地事务 + 消息表 + 消息队列。业务操作和"记录消息"在同一个本地事务，再由后台任务把消息发送到 MQ，消费者幂等处理。这是电商最常用的方案。

```
本地事务：
  UPDATE 扣库存
  INSERT 业务消息到 local_message 表
COMMIT
-- 后台任务扫描 local_message 表，发送到 MQ，发送成功后标记已发送
-- 消费者幂等消费，完成后续操作
```

> 前端类比：最终一致性像"发邮件确认"。你提交表单后系统先记一条"待发邮件"记录（和业务数据一起落库），后台慢慢发邮件。即使邮件服务暂时不可用，业务也不阻塞，邮件最终会发出去。这和前端的"乐观 UI + 后台同步"思路一致。

#### 6.6.5 分布式锁与事务的配合：Redis 锁保护数据库操作的经典模式

在秒杀、抢红包等高并发场景，经典模式是"Redis 分布式锁（或 Redis 预扣）+ 数据库事务"。

模式一：Redis 锁做并发入口限流

```
请求 -> Redis SETNX 获取锁 -> 成功则进入数据库事务扣减 -> 释放锁
                          -> 失败则快速拒绝（库存不足/繁忙提示）
```

Redis 锁的作用是"减少数据库并发量"，让同一资源的并发请求串行化进入数据库。但数据库层仍需行锁/乐观锁作为最后防线，因为：
- Redis 锁有超时自动释放，可能出现"锁失效但事务未完成"的窗口。
- 分布式环境下 Redis 锁不是绝对可靠（主从切换可能丢锁）。

模式二：Redis 预扣库存 + 异步落库（最终一致性）

```
请求 -> Redis Lua 原子扣减预库存 -> 成功则发 MQ 消息 -> 返回"抢购成功"
                                  -> 失败则返回"售罄"
MQ 消费者 -> 数据库事务内创建订单、扣减 DB 库存（乐观锁兜底）
```

这种模式下，数据库压力被 MQ 削峰，扛住秒杀流量。但引入了 Redis-MQ-DB 的一致性复杂度（Redis 扣减成功但 MQ/DB 失败需补偿）。

**关键原则**：分布式锁/Redis 预扣是"性能优化层"，数据库事务是"正确性保证层"。任何分布式锁都不能替代数据库事务——锁可能失效，事务的 ACID 是数据一致性的最后防线。设计时永远假设"锁可能失效"，数据库层必须有兜底。

```python
# 伪代码：Redis 锁 + 数据库事务的完整模式
import redis, json, time

r = redis.Redis()

def seckill(product_id, user_id, qty):
    lock_key = f"lock:seckill:{product_id}"

    # 1. Redis 分布式锁（防并发入口）
    token = str(time.time())
    if not r.set(lock_key, token, nx=True, px=5000):
        return {"code": 503, "msg": "system busy"}

    try:
        # 2. 数据库事务（正确性保证）
        with db.cursor() as cur:
            cur.execute("SELECT stock, version FROM products WHERE id=%s FOR UPDATE",
                        (product_id,))
            row = cur.fetchone()
            if not row or row['stock'] < qty:
                return {"code": 400, "msg": "out of stock"}
            cur.execute(
                "UPDATE products SET stock=stock-%s, version=version+1 WHERE id=%s",
                (qty, product_id)
            )
            cur.execute(
                "INSERT INTO orders(user_id, status) VALUES(%s,'PAID')",
                (user_id,)
            )
        db.commit()
        return {"code": 200, "msg": "success"}
    except Exception as e:
        db.rollback()
        return {"code": 500, "msg": str(e)}
    finally:
        # 3. 释放锁（用 Lua 保证只删自己的锁，防误删别人的锁）
        r.eval(
            "if redis.call('get', KEYS[1])==ARGV[1] then "
            "  return redis.call('del', KEYS[1]) "
            "else return 0 end",
            1, lock_key, token
        )
```

释放锁用 Lua 脚本"先 GET 比对再 DEL"是为了防止误删别人的锁——如果自己的锁已超时被自动释放，别的请求又拿了同一把锁，此时直接 DEL 会删掉别人的锁。Lua 脚本保证 GET 和 DEL 的原子性。

> 总结：对于前端转后端的开发者，事务是从"内存状态"思维转向"持久化一致性"思维的关键。前端的 Promise.all 能保证"全部成功或报错"，但已执行的 HTTP 请求无法撤销；数据库事务的 ACID 能保证"已执行的也能回滚"，这是后端数据可靠性的根基。并发控制（锁/MVCC/乐观锁/悲观锁/分布式锁）则是保障高并发下正确性的工具集，需要根据并发量级和冲突频率选择合适的策略。理解这些底层机制，才能在后端开发中写出既高效又可靠的数据访问代码。

---

> 本篇（第五章 + 第六章）完。下一篇将进入索引优化与性能调优、Python 数据库访问层（SQLAlchemy / Tortoise ORM）等内容。
