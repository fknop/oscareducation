# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, Client, RequestFactory

import json

from forum.views import forum_dashboard, thread as get_thread, get_skills
from promotions.models import Lesson, Stage
from users.models import Professor, Student
from skills.models import Skill, Section
from .models import Thread, Message
from .views import deepValidateAndFetch
from dashboard import private_threads, public_class_threads, public_teacher_threads_student, get_thread_set
from views import create_thread, reply_thread


class FakeRequest:
    def __init__(self, user):
        self.user = user

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

        self.fourth_thread = Thread(title="Information regarding spam", author=self.teacher_user,
                                    professor=self.teacher)
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


class TestGetThread(TestCase):
    def setUp(self):
        self.user = User(username="user_auth")
        self.user.set_password('12345')
        self.user.save()

        self.c = Client()
        self.c.login(username='user_auth', password='12345')

    def test_get_thread_page_404(self):
        response = self.c.get('/forum/thread/150')
        self.assertEquals(response.status_code, 404)

    def test_get_thread_page(self):
        user = User()
        user.save()

        thread = Thread(title="test", author=user)
        thread.save()

        first_message = Message(author=user, thread=thread, content="hello")
        first_message.save()

        response = self.c.get('/forum/thread/' + str(thread.id))
        context = response.context
        self.assertEquals(context["thread"], thread)
        self.assertEquals(context["messages"][0], thread.messages()[0])
        self.assertEquals(response.status_code, 200)


class TestPostReply(TestCase):
    def setUp(self):
        self.first_user = User(username="Alice")
        self.first_user.set_password('12345')
        self.first_user.save()
        self.second_user = User(username="Bob")
        self.second_user.save()
        self.third_user = User(username="Trudy")
        self.third_user.save()
        self.first_student = Student(user=self.first_user)
        self.first_student.save()
        self.second_student = Student(user=self.second_user)
        self.second_student.save()
        self.teacher = Professor(user=self.third_user)
        self.teacher.save()
        self.stage = Stage(id=1, name="Stage1", level=1)
        self.stage.save()
        self.lesson = Lesson(id=1, name="Lesson 1", stage_id=1)
        self.lesson.save()
        self.thread_lesson = Thread.objects.create(author=self.first_user, lesson=self.lesson, title="Thread 1", id=1)
        self.thread_lesson.save()
        self.thread_id = self.thread_lesson.id
        self.message = Message.objects.create(author=self.first_user, content="Content of message",
                                              thread=self.thread_lesson)
        self.message.save()
        self.c = Client()
        self.c.login(username='Alice', password='12345')

    def test_get_thread_page(self):
        response = self.c.get('/forum/thread/{}'.format(self.thread_id))
        self.assertEquals(response.status_code, 200)

    def test_reply_thread(self):
        content = 'content of the new message'
        response = self.c.post('/forum/thread/{}'.format(self.thread_id), data={'content': content})

        messages = Message.objects.all().filter(thread=self.thread_lesson)

        self.assertEquals(messages.last().content, content)
        self.assertEquals(response.status_code, 302)  # 302 because redirects


class TestPostThread(TestCase):
    def setUp(self):
        self.user1 = User(username='Michel')
        self.user1.set_password('12345')
        self.user1.save()
        self.teacher = Professor(user=self.user1)
        self.teacher.save()
        self.user2 = User(username="Trudy")
        self.user2.save()
        self.student = Student(user=self.user2)
        self.student.save()
        self.stage = Stage(id=1, name="Stage1", level=1)
        self.stage.save()
        self.lesson = Lesson(id=1, name="Lesson 1", stage_id=1)
        self.lesson.save()
        self.skill1 = Skill(code=422230, name="Compter deux par deux", description="")
        self.skill1.save()
        self.skill2 = Skill(code=422231, name="Lacer ses chaussures", description="")
        self.skill2.save()
        self.c = Client()
        self.c.login(username='Michel', password='12345')

    def test_post_valid_new_public_thread(self):
        new_thread = {
            "title": "titre_1",
            "visibdata": str(self.teacher.id),
            "skills": [422230, 422231],
            "content": "message_1",
            "visibility": "public"
        }
        response = self.c.post('/forum/write/', data=new_thread)
        new_thread = Thread.objects.order_by('-pk')[0]
        last_msg = Message.objects.order_by('-pk')[0]
        self.assertEquals(response.status_code, 302)
        self.assertEquals(new_thread.title, "titre_1")
        self.assertEquals(last_msg.content, "message_1")

    def test_post_valid_new_private_thread(self):
        new_thread = {
            "title": "titre_2",
            "visibdata": str(self.user2.id),
            "skills": [422230, 422231],
            "content": "message_2",
            "visibility": "private"
        }
        response = self.c.post('/forum/write/', data=new_thread)
        new_thread = Thread.objects.order_by('-pk')[0]
        last_msg = Message.objects.order_by('-pk')[0]
        self.assertEquals(response.status_code, 302)
        self.assertEquals(new_thread.title, "titre_2")
        self.assertEquals(last_msg.content, "message_2")

    def test_post_valid_new_class_thread(self):
        new_thread = {
            "title": "titre_3",
            "visibdata": str(self.lesson.id),
            "skills": [422230, 422231],
            "content": "message_3",
            "visibility": "class"
        }
        response = self.c.post('/forum/write/', data=new_thread)
        new_thread = Thread.objects.order_by('-pk')[0]
        last_msg = Message.objects.order_by('-pk')[0]
        self.assertEquals(response.status_code, 302)
        self.assertEquals(new_thread.title, "titre_3")
        self.assertEquals(last_msg.content, "message_3")

    def test_post_invalid_new_thread_blank_req_fields(self):
        thread_cnt_before = Thread.objects.all().count()
        msg_cnt_before = Message.objects.all().count()
        new_thread = {
            "title": "",
            "visibdata": "",
            "skills": "",
            "content": "",
            "visibility": ""
        }
        response = self.c.post('/forum/write/', data=new_thread)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(thread_cnt_before, Thread.objects.all().count())
        self.assertEquals(msg_cnt_before, Message.objects.all().count())

    def test_post_invalid_new_thread_unknown_skills(self):
        thread_cnt_before = Thread.objects.all().count()
        msg_cnt_before = Message.objects.all().count()
        new_thread = {
            "title": "titre_5",
            "visibdata": str(self.lesson.id),
            "skills": ["l", "m"],
            "content": "message_5",
            "visibility": "class"
        }
        response = self.c.post('/forum/write/', data=new_thread)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(thread_cnt_before, Thread.objects.all().count())
        self.assertEquals(msg_cnt_before, Message.objects.all().count())

    def test_post_invalid_new_private_thread_unknown_recipient(self):
        thread_cnt_before = Thread.objects.all().count()
        msg_cnt_before = Message.objects.all().count()
        new_thread = {
            "title": "titre_6",
            "visibdata": "unknown",
            "skills": "422230 422231",
            "content": "message_6",
            "visibility": "private"
        }
        response = self.c.post('/forum/write/', data=new_thread)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(thread_cnt_before, Thread.objects.all().count())
        self.assertEquals(msg_cnt_before, Message.objects.all().count())

    def test_post_invalid_new_class_thread_unknown_class(self):
        thread_cnt_before = Thread.objects.all().count()
        msg_cnt_before = Message.objects.all().count()
        new_thread = {
            "title": "titre_7",
            "visibdata": "unknown",
            "skills": [422230, 422231],
            "content": "message_7",
            "visibility": "class"
        }
        response = self.c.post('/forum/write/', data=new_thread)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(thread_cnt_before, Thread.objects.all().count())
        self.assertEquals(msg_cnt_before, Message.objects.all().count())

    def test_post_invalid_new_public_thread_unknown_professor(self):
        thread_cnt_before = Thread.objects.all().count()
        msg_cnt_before = Message.objects.all().count()
        new_thread = {
            "title": "titre_8",
            "visibdata": "unknown",
            "skills": [422230, 422231],
            "content": "message_7",
            "visibility": "public"
        }
        response = self.c.post('/forum/write/', data=new_thread)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(thread_cnt_before, Thread.objects.all().count())
        self.assertEquals(msg_cnt_before, Message.objects.all().count())


class TestGetWritePage(TestCase):
    def setUp(self):
        self.user = User(username='auth_user')
        self.user.set_password('12345')
        self.user.save()
        self.c = Client()
        self.c.login(username='auth_user', password='12345')

    def test_get_write_page(self):
        response = self.c.get('/forum/write/')
        self.assertEquals(response.status_code, 200)


class TestMisc(TestCase):
    def setUp(self):
        self.user = User(username="Brandon")
        self.user.set_password('12345')
        self.user.save()
        self.second_user = User(username="Kevin")
        self.second_user.set_password('12345')
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

        self.skill1 = Skill(id=1, name="Skill1", code="1")
        self.skill1.save()

        self.skill2 = Skill(id=2, name="Skill2", code="2")
        self.skill2.save()

        self.section = Section(id=1, name="Section1")
        self.section.save()

        self.skill3 = Skill(id=3, name="Skill3", code="3")
        self.skill3.section = self.section
        self.skill3.save()

        self.skill4 = Skill(id=4, name="Skill4", code="4")
        self.skill4.section = self.section
        self.skill4.save()

        self.stage = Stage(id=1, name="Stage1", level=1)
        self.stage.save()
        self.stage.skills.add(self.skill1)
        self.stage.skills.add(self.skill2)
        self.stage.save()

        self.second_stage = Stage(id=2, name="Stage2", level=1)
        self.second_stage.save()
        self.second_stage.skills.add(self.skill3)
        self.second_stage.skills.add(self.skill4)
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

        self.fourth_thread = Thread(title="Information regarding spam", author=self.teacher_user,
                                    professor=self.teacher)
        self.fourth_thread.save()


        self.c1 = Client()
        self.c1.login(username=self.user.username, password='12345')

        self.c2 = Client()
        self.c2.login(username=self.second_user.username, password='12345')

    def test_get_skills_user(self):
        skills, sections = get_skills(FakeRequest(self.user))
        self.assertEquals(len(skills), 2)

        self.assertListEqual(skills, [self.skill1, self.skill2])
        self.assertEquals(len(sections), 0)

    def test_get_skills_second_user(self):
        skills, sections = get_skills(FakeRequest(self.second_user))
        self.assertEquals(len(skills), 4)
        self.assertListEqual(skills, [self.skill1, self.skill2, self.skill3, self.skill4])

        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0], self.skill3.section)

    def test_get_professors_user(self):
        response = self.c1.get('/forum/write/professors/')
        json_data = json.loads(response.content)
        data = json_data["data"]

        professor = data[0]
        self.assertEquals(len(data), 1)
        self.assertEquals(professor, {
            "id": self.teacher.id,
            "username": self.teacher.user.username,
            "first_name": self.teacher.user.first_name,
            "last_name": self.teacher.user.last_name
        })

    def test_get_professors_second_user(self):
        response = self.c2.get('/forum/write/professors/')
        json_data = json.loads(response.content)
        data = json_data["data"]
        professor = data[0]
        self.assertEquals(len(data), 1)
        self.assertEquals(professor, {
            "id": self.teacher.id,
            "username": self.teacher.user.username,
            "first_name": self.teacher.user.first_name,
            "last_name": self.teacher.user.last_name
        })

    def test_get_lessons_user(self):
        response = self.c1.get('/forum/write/lessons/')
        json_data = json.loads(response.content)
        data = json_data["data"]
        self.assertEquals(len(data), 1)

        lesson = data[0]
        self.assertEqual(lesson["id"], self.lesson.id)
        self.assertEqual(lesson["name"], self.lesson.name)

    def test_get_lessons_second_user(self):
        response = self.c2.get('/forum/write/lessons/')
        json_data = json.loads(response.content)
        data = json_data["data"]

        self.assertEquals(len(data), 2)

        lesson = data[0]
        self.assertEqual(lesson["id"], self.lesson.id)
        self.assertEqual(lesson["name"], self.lesson.name)

        lesson2 = data[1]
        self.assertEqual(lesson2["id"], self.second_lesson.id)
        self.assertEqual(lesson2["name"], self.second_lesson.name)

    def test_get_users(self):
        response = self.c1.get('/forum/write/users/')
        json_data = json.loads(response.content)
        data = json_data["data"]
        users = User.objects.all()
        for i, user in enumerate(data):
            self.assertEquals(user, {
                'id': users[i].id,
                'username': users[i].username,
                'first_name': users[i].first_name,
                'last_name': users[i].last_name
            })


