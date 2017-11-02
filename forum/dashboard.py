from models import Thread
from promotions.models import Lesson
from users.models import Student, Professor
from django.db.models import Q


def private_threads(user):
    """Returns the private messages of a student or a teacher"""
    threads = Thread.objects.filter(Q(author=user) | Q(recipient=user))
    pri_threads = set()
    for t in threads:
        if t.is_private():
            pri_threads.add(t)
    return pri_threads


def public_teacher_threads_student(user):
    """Returns the public threads of a student linked to a teacher"""
    pub_threads = set()
    lessons = user.lesson_set.all()

    for lesson in lessons:
        for prof in lesson.professors.all():
            threads = Thread.objects.filter(Q(professor=prof))
            for t in threads:
                pub_threads.add(t)
    return pub_threads


def public_teacher_threads_teacher(user):
    pub_threads = set()
    threads = Thread.objects.filter(professor=user)
    for t in threads:
        pub_threads.add(t)
    return pub_threads


def public_class_threads(user):
    """Returns the public threads of a student or teacher linked to a lesson"""
    pub_threads = set()
    lessons = user.lesson_set.all()

    for l in lessons:
        threads = Thread.objects.filter(Q(lesson=l))
        for t in threads:
            pub_threads.add(t)
    return pub_threads


def get_thread_set(user):
    """Returns the list of all accessible threads"""
    thread_set = set()
    if Student.objects.filter(user=user).exists():
        student = Student.objects.get(user=user)
        thread_set.update(private_threads(user))
        thread_set.update(public_teacher_threads_student(student))
        thread_set.update(public_class_threads(student))
    elif Professor.objects.filter(user=user).exists():
        professor = Professor.objects.get(user=user)
        thread_set.update(private_threads(user))
        thread_set.update(public_teacher_threads_teacher(professor))
        thread_set.update(public_class_threads(professor))
    return thread_set
