person = {
    'first_name': 'Beneath',
    'last_name': 'Yetta',
    'age': 250,
    'country': '芬兰',
    'is_married': True,
    'skills': ['JavaScript', 'React', 'Node', 'MongoDB', 'Python', "Django"],
    'address': {
        'street': '太空街',
        'zipcode': '02210'
    }
}

# 检查字典中是否有 skills 键，如果有则打印 skills 列表和中间技能
if 'skills' in person and person['skills']:
    skills = person['skills']
    print(f"当前用户的技能有：{skills}")

    if len(skills) % 2 == 1:  # noqa
        middle_index = len(skills) // 2  # noqa
        print(f"中间技能是：{skills[middle_index]}")  # noqa
    else:
        right_index = len(skills) // 2  # noqa
        left_index = right_index - 1
        print(f"中间技能是：{skills[left_index]} 和 {skills[right_index]}")  # noqa
else:
    print("当前用户没有 skills 信息")

# 检查是否在字典中有 skills 键，如果有则检查该人是否具备'Python'技能并打印结果
if 'skills' in person:
    if 'Python' in person['skills']:  # noqa
        print("这个人有 Python 技能。")
    else:
        print("这个人没有 Python 技能。")

"""
如果一个人的技能只有 JavaScript 和 React，打印('他是前端开发者')，如果一个人的技能有 Node、Python、MongoDB，打印('他是后端开发者')，
如果一个人的技能有 React、Node 和 MongoDB，打印('他是全栈开发者')
，否则打印'未知头衔' - 为获得更准确的结果，可以嵌套更多条件！
"""
if 'skills' in person:
    skills_set = set(person['skills'])  # noqa
    frontend_skills = {'JavaScript', 'React'}
    backend_skills = {'Node', 'Python', 'MongoDB'}
    fullstack_skills = {'React', 'Node', 'MongoDB'}

    if skills_set == frontend_skills:
        print('他是前端开发者')
    elif fullstack_skills.issubset(skills_set):
        print('他是全栈开发者')
    elif backend_skills.issubset(skills_set):
        print('他是后端开发者')
    else:
        print('未知头衔')

# 如果该人结婚了且居住在芬兰，按以下格式打印信息
if person["is_married"] and person["country"] == "芬兰":
    print(f"{person['first_name']} {person['last_name']} 住在{person["country"]}。他已婚。")
