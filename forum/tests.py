# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, Client, RequestFactory

from forum.views import forum_dashboard
from promotions.models import Lesson, Stage
from users.models import Professor, Student
from .models import Thread, Message
from dashboard import private_threads, public_class_threads, public_teacher_threads_student, get_thread_set


class ThreadModelTest(TestCase):

    def test_invalid_thread_both_recipient_professor(self):
        user = User(username="sender")
        user.save()

        recipient = User(username="recipient")
        recipient.save()

        professor_user = User(username="professor")
        professor_user.save()
        professor = Professor(user=professor_user)
        professor.save()

        thread = Thread(title="Help", author=user, recipient=recipient, professor=professor)

        with self.assertRaises(ValidationError):
            thread.clean()

    def test_create_thread(self):
        user = User()
        user.save()
        thread = Thread(title="Help on Calculus", author=user)
        thread.save()

        self.assertEquals(thread.title, "Help on Calculus")

        thread.title = "Help"
        thread.save()

        self.assertEquals(thread.title, "Help")

    def test_private_thread(self):
        user = User(username="sender")
        user.save()

        recipient = User(username="recipient")
        recipient.save()

        thread = Thread(title="Help", author=user, recipient=recipient)
        thread.clean()
        thread.save()

        self.assertTrue(thread.is_private())
        self.assertFalse(thread.is_public_lesson())
        self.assertFalse(thread.is_public_professor())

    def test_public_professor_thread(self):
        user = User(username="sender")
        user.save()

        professor_user = User(username="professor")
        professor_user.save()
        professor = Professor(user=professor_user)
        professor.save()

        thread = Thread(title="Help", author=user, professor=professor)
        thread.clean()
        thread.save()

        self.assertTrue(thread.is_public_professor())
        self.assertFalse(thread.is_private())
        self.assertFalse(thread.is_public_lesson())

    def test_public_lesson_thread(self):
        user = User(username="sender")
        user.save()

        stage = Stage(level=1)
        stage.save()

        lesson = Lesson(name="Calculus", stage=stage)
        lesson.save()

        thread = Thread(title="Help", author=user, lesson=lesson)
        thread.clean()
        thread.save()


        self.assertTrue(thread.is_public_lesson())
        self.assertFalse(thread.is_private())
        self.assertFalse(thread.is_public_professor())

    def test_messages(self):
        user = User()
        user.save()

        thread = Thread(title="test", author=user)
        thread.save()

        first_message = Message(author=user, thread=thread, content="hello")
        first_message.save()

        second_message = Message(author=user, thread=thread, content="hello as well")
        second_message.save()

        messages = thread.messages()

        self.assertEquals(messages[0].id, first_message.id)
        self.assertEquals(messages[1].id, second_message.id)

    def test_replies(self):
        user = User()
        user.save()

        thread = Thread(title="test", author=user)
        thread.save()

        first_message = Message(author=user, thread=thread, content="hello")
        first_message.save()

        second_message = Message(author=user, thread=thread, content="hello as well", parent_message=first_message)
        second_message.save()

        messages = thread.messages()

        self.assertEquals(messages[0], first_message)

        replies = first_message.replies()
        self.assertEquals(replies[0], second_message)

        replies_with_self = first_message.replies(include_self=True)
        self.assertEquals(replies_with_self[0], first_message)
        self.assertEquals(replies_with_self[1], second_message)

class TestGetDashboard(TestCase):
    def setUp(self):
        self.user = User(username="Brandon")
        self.user.save()
        self.second_user = User(username="Kevin")
        self.second_user.save()
        self.teacher_user = User(username="Vince")
        self.teacher_user.save()
        self.second_teacher_user = User(username="Nicolas")
        self.second_teacher_user.save()

        self.student = Student(user=self.user)
        self.student.save()
        self.second_student = Student(user=self.second_user)
        self.second_student.save()
        self.teacher = Professor(user=self.teacher_user)
        self.teacher.save()
        self.second_teacher = Professor(user=self.second_teacher_user)
        self.second_teacher.save()

        self.stage = Stage(id=1, name="Stage1", level=1)
        self.stage.save()
        self.second_stage = Stage(id=2, name="Stage2", level=1)
        self.second_stage.save()

        self.lesson = Lesson(id=1, name="English", stage_id=1)
        self.lesson.save()
        self.lesson.students.add(self.student)
        self.lesson.students.add(self.second_student)
        self.lesson.professors.add(self.teacher)
        self.lesson.save()

        self.second_lesson = Lesson(id=2, name="French", stage_id=2)
        self.second_lesson.save()
        self.second_lesson.students.add(self.second_student)
        self.second_lesson.professors.add(self.teacher)
        self.second_lesson.save()

        self.thread = Thread(title="Help", author=self.user, recipient=self.teacher_user)
        self.thread.save()

        self.second_thread = Thread(title="Send help", author=self.second_user, lesson=self.second_lesson)
        self.second_thread.save()

        self.third_thread = Thread(title="Information regarding w/e", author=self.teacher_user, professor=self.teacher)
        self.third_thread.save()

        self.fourth_thread = Thread(title="Information regarding spam", author=self.teacher_user, professor=self.teacher)
        self.fourth_thread.save()

    # TODO
    def test_forum_dashboard(self):
        factory = RequestFactory()
        request = factory.get("/forum/")
        request.user = self.user
        response = forum_dashboard(request)
        self.assertEquals(response.status_code, 200)

    def test_private_dashboard_empty(self):
        user = User(username="Jimmy")
        user.save()
        result = private_threads(user)
        expected = set()
        self.assertEquals(expected, result)

    def test_private_dashboard(self):
        result = private_threads(self.user)
        expected = set()
        expected.add(self.thread)
        self.assertEquals(expected, result)

    def test_public_class_dashboard_empty(self):
        user = User(username="Jimmy")
        user.save()
        student = Student(user=user)
        student.save()
        result = public_class_threads(student)
        expected = set()
        self.assertEquals(expected, result)

    def test_public_class_dashboard(self):
        result = public_class_threads(self.second_student)
        expected = set()
        expected.add(self.second_thread)
        self.assertEquals(expected, result)

    def test_public_teacher_dashboard_empty(self):
        user = User(username="Jimmy")
        user.save()
        student = Student(user=user)
        student.save()
        result = public_teacher_threads_student(student)
        expected = set()
        self.assertEquals(expected, result)

    def test_public_class_dashboard_teacher(self):
        result = public_teacher_threads_student(self.teacher)
        expected = set()
        expected.add(self.third_thread)
        expected.add(self.fourth_thread)
        self.assertEquals(expected, result)

    def test_get_thread_set_teacher(self):
        result = get_thread_set(self.teacher_user)
        expected = set()
        expected.add(self.thread)
        expected.add(self.second_thread)
        expected.add(self.third_thread)
        expected.add(self.fourth_thread)
        self.assertEquals(expected, result)

    """
    def test_public_class_dashboard_empty(self):
        user = User(username="Jean-Mi")
        user.save()
        professor = Professor(user=user)
        professor.save()
        result = public_class_threads(professor)
        expected = set()
        self.assertEquals(expected, result)

    def test_public_class_dashboard_teacher(self):
        result = public_class_threads(self.teacher)
        expected = set()
        expected.add(self.second_thread)
        self.assertEquals(expected, result)

    def test_public_teacher_dashboard_empty_teacher(self):
        user = User(username="Jean-Mi")
        user.save()
        professor = Professor(user=user)
        professor.save()
        result = public_teacher_threads_student(professor)
        expected = set()
        self.assertEquals(expected, result)

    def test_public_class_dashboard_teacher(self):
        result = public_teacher_threads_student(self.teacher)
        expected = set()
        expected.add(self.third_thread)
        expected.add(self.fourth_thread)
        self.assertEquals(expected, result)
"""


class TestGetThread(TestCase):
    def test_get_thread_page_404(self):
        c = Client()

        # Unknown ID
        response = c.get('/forum/thread/150')
        self.assertEquals(response.status_code, 404)

    def test_get_thread_page(self):
        c = Client()
        user = User()
        user.save()

        thread = Thread(title="test", author=user)
        thread.save()

        first_message = Message(author=user, thread=thread, content="hello")
        first_message.save()
        response = c.get('/forum/thread/' + str(thread.id))
        context = response.context
        self.assertEquals(context["thread"], thread)
        self.assertEquals(context["messages"][0], thread.messages()[0])
        self.assertEquals(response.status_code, 200)


class TestPostReply(TestCase):
    def test_get_thread_page(self):
        c = Client()
        # TODO: temporary id for temporary test
        response = c.post('/forum/thread/1')
        self.assertEquals(response.status_code, 200)


class TestPostThread(TestCase):
    def test_post_thread(self):
        c = Client()
        # TODO: temporary id for temporary test
        response = c.post('/forum/write/')
        self.assertEquals(response.status_code, 200)


class TestGetWritePage(TestCase):
    def test_get_write_page(self):
        c = Client()
        response = c.get('/forum/write/')
        self.assertEquals(response.status_code, 200)
