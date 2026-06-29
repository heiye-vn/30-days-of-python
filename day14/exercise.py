import os
import sys
from collections import Counter

# 获取当前文件所在目录的上一级目录（即项目根目录），并将其绝对路径加入到 sys.path 中
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 现在可以正常导入 data 目录下的 countries_data 模块了
from data.countries_data import countries_data

# 测试是否成功获取数据
if __name__ == "__main__":
    print(f"成功导入数据！共有 {len(countries_data)} 个国家的数据。")
    # 打印第一个国家的数据作为示例
    print("示例数据:", countries_data[0])


# 1. 按国家名称、首都和人口排序国家
def sort_countries_by_name_capital_population(countries):
    return sorted(countries, key=lambda x: (x["name"], x["capital"], x["population"]))


sorted_countries = sort_countries_by_name_capital_population(countries_data)
# print(sorted_countries)


# 2. 按位置排序出前十个最常用语言
# 方法一
def get_top_10_languages(countries):
    languages = []
    for country in countries:
        # 使用 extend 代替内存循环，提升追加效率
        languages.extend(country["languages"])

    # 使用 Counter 快速统计频次并去重
    language_counts = Counter(languages)

    # most_common(10) 返回前十个最常出现的（语言, 频次）元组列表
    top_10 = language_counts.most_common(10)

    # return top_10
    return [lang_name.capitalize() for lang_name, count in top_10]


print(get_top_10_languages(countries_data))


# 方法二
def get_top_10_languages3(countries):
    languages = []
    for country in countries:
        languages.extend(country["languages"])

    # 使用 dict 统计频次并去重
    counts = {}
    for lang in languages:
        counts[lang] = counts.get(lang, 0) + 1  # 使用 get 方法获取当前语言的频次并加一

    return sorted(counts, key=lambda lang_: counts[lang_], reverse=True)[:10]


print(get_top_10_languages3(countries_data))


# 3. 排序出前十个人口最多的国家
def get_top_10_countries_by_population(countries):
    return sorted(countries, key=lambda x: x["population"], reverse=True)[:10]


top_10_countries = get_top_10_countries_by_population(countries_data)
# print(top_10_countries)
