"""
编写一个 Python 脚本，显示以下表格

1 1 1 1 1
2 1 2 4 8
3 1 3 9 27
4 1 4 16 64
5 1 5 25 125
"""

# for i in range(1, 6):
#     for j in range(1, 6):
#         if i == 1:
#             print(i, end=" ")
#         else:
#             if j == 1:
#                 print(i, end=" ")
#             else:
#                 print(i ** (j - 2), end=" ")
#     print()

# for i in range(1, 6):
#     print(i, 1, i, i ** 2, i ** 3)

for i in range(1, 6):
    for j in range(1, 6):
        # 三元表达式：当 j == 1 时输出 i，否则输出 i ** (j - 2)
        val = i if j == 1 else i ** (j - 2)
        print(val, end=" ")
    print()
