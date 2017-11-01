# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, Client

from promotions.models import Lesson, Stage
from users.models import Professor
from .models import Thread, Message


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
    # TODO
    def test_forum_dashboard(self):
        c = Client()
        response = c.get("/forum/")
        self.assertEquals(response.status_code, 200)


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
        # TODO: temporary id for temporary test
        response = c.get('/forum/write/')
        self.assertEquals(response.status_code, 200)
