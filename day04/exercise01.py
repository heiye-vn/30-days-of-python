# 1. 判断文件类型
# filename = 'photo.png'
#
# if filename.endswith('.png'):
#     print('这是 PNG 类型图片')

# 2. 提取文件扩展名
filename2 = 'report.pdf'
extension = filename2.split('.')[-1]
# print(extension)

# 3. 反转字符串
text = 'python'
# print(text[::-1])

# 4. 统计单词出现次数
# 注：不能直接使用字符串的 count() 方法来统计，因为 count() 方法是统计子字符串出现的次数，而不是单词出现的次数。
sentence = "apple banana apple orange apple"
words = sentence.split()
# print(words.count("apple"))

# 5. 为字符串 'Python For Everyone' 创建首字母缩略词或缩写
textStr = 'Python For Everyone'
# 将字符串拆分成单词列表
wordList = textStr.split()
# 提取每个单词的首字母并转为大写
# 将它们拼接在一起
acronym = "".join([word[0].upper() for word in wordList])
print(acronym)
