# 1. 判断文件类型
# filename = 'photo.png'
#
# if filename.endswith('.png'):
#     print('这是 PNG 类型图片')

# 2. 提取文件扩展名
filename2 = 'report.pdf'
extension = filename2.split('.')[-1]
print(extension)

# 3. 反转字符串
text = 'python'
print(text[::-1])

# 4. 统计单词出现次数
# 注：不能直接使用字符串的 count() 方法来统计，因为 count() 方法是统计子字符串出现的次数，而不是单词出现的次数。
sentence = "apple banana apple orange apple"
words = sentence.split()
print(words.count("apple"))
