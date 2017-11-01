from models import Thread
from promotions.models import Lesson
from users.models import Student, Professor
from django.db.models import Q


def private_threads(user):
    threads = Thread.objects.filter(Q(author=user) | Q(recipient=user))
    pri_threads = set()
    for t in threads:
        if t.is_private():
            pri_threads.add(t)
    return pri_threads


def public_teacher_threads(user):
    pub_threads = set()
    student = Student.objects.get(user=user)
    lessons = student.lesson_set.all()
    for lesson in lessons:
        for prof in lesson.professors.all():
            threads = Thread.objects.filter(Q(professor=prof))
            for t in threads:
                if t.is_public_professor():
                    pub_threads.add(t)
    return pub_threads


def public_class_threads(user):
    pub_threads = set()
    student = Student.objects.get(user=user)
    lessons = student.lesson_set.all()

    for l in lessons:
        threads = Thread.objects.filter(Q(lesson=l))
        for t in threads:
            if t.is_public_lesson():
                pub_threads.add(t)
    return pub_threads

