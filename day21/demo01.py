"""
综合案例：学生管理系
结合类、对象、实例方法、类方法、封装、魔术方法等组合
"""


class Student:
    school = "University of California"

    def __init__(self, student_id, name, age, score):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.score = score

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        if not 0 <= value <= 100:
            raise ValueError("成绩必须在 0 到 100 之间")
        self._score = value

    def is_passed(self):
        return self.score >= 60

    def update_score(self, score):
        self.score = score

    def __str__(self):
        status = "及格" if self.is_passed() else "不及格"
        return f"{self.student_id} - {self.name} - {self.score} 分 - {status}"


class StudentManager:
    def __init__(self):
        self.students = {}

    # 添加学生
    def add_student(self, student):  # noqa
        if student.student_id in self.students:
            raise ValueError("学生编号已存在")
        self.students[student.student_id] = student

    # 删除学生
    def remove_student(self, student_id):
        if student_id not in self.students:
            raise KeyError("学生不存在")
        del self.students[student_id]

    # 修改学生信息
    def update_student(self, student_id, name, age, score):
        if student_id not in self.students:
            raise KeyError("学生不存在")
        modify_student = self.students[student_id]
        modify_student.name = name
        modify_student.age = age
        modify_student.score = score
        return modify_student

    # 查询学生
    def find_student(self, student_id):
        target_student = self.students.get(student_id)
        if not target_student:
            raise KeyError("学生不存在")
        else:
            return target_student

    # 列出所有学生
    def list_students(self):
        return list(self.students.values())

    # 获取平均分
    def average_score(self):
        if not self.students:
            return 0
        total = sum(student.score for student in self.students.values())  # noqa
        return total / len(self.students)


manager = StudentManager()

try:
    manager.add_student(Student("S001", "Alice", 18, 95))
    manager.add_student(Student("S002", "Bob", 19, 58))
    manager.add_student(Student("S003", "Charlie", 18, 82))
    manager.add_student(Student("S004", "Rose", 18, 110))
except ValueError as e:
    print(f"添加失败：{e}")
else:
    print("学生添加成功")


for student in manager.list_students():
    print(student)

# print(f"平均分：{manager.average_score():.2f}")

try:
    student = manager.find_student("S004")
    if student:
        student.update_score(66)  # noqa
        print(student)
except KeyError as e:
    print(f"查询失败：{e}")
