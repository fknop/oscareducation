# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.test import TestCase

from promotions.models import Lesson, Stage
from users.models import Professor
from .models import Thread, Message


class ThreadModelTest(TestCase):
    def testCreateThread(self):
        user = User()
        user.save()
        thread = Thread(title="Help on Calculus", author=user)
        thread.save()

        self.assertEquals(thread.title, "Help on Calculus")

        thread.title = "Help"
        thread.save()

        self.assertEquals(thread.title, "Help")

    def testPrivate(self):
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


    def testPublicProfessor(self):
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

    def testPublicLesson(self):
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

    def testMessages(self):
        user = User()
        user.save()

        thread = Thread(title="test", author=user)
        thread.save()

        first_message = Message(thread=thread, content="hello")
        first_message.save()

        second_message = Message(thread=thread, content="hello as well")
        second_message.save()

        messages = thread.messages()

        self.assertEquals(messages[0].id, first_message.id)
        self.assertEquals(messages[1].id, second_message.id)

    def testReplies(self):
        user = User()
        user.save()

        thread = Thread(title="test", author=user)
        thread.save()

        first_message = Message(thread=thread, content="hello")
        first_message.save()

        second_message = Message(thread=thread, content="hello as well", parent_message=first_message)
        second_message.save()

        messages = thread.messages()

        self.assertEquals(messages[0].id, first_message.id)
        self.assertEquals(messages[1].id, second_message.id)

        replies = first_message.replies()
        self.assertEquals(replies[0], second_message)

        all_replies = first_message.all_replies()
        self.assertEquals(all_replies[first_message], [{second_message: []}])


    def testAllReplies(self):
        user = User()
        user.save()

        thread = Thread(title="test", author=user)
        thread.save()

        first_message = Message(thread=thread, content="hello")
        first_message.save()

        second_message = Message(thread=thread, content="hello as well", parent_message=first_message)
        second_message.save()

        third_message = Message(thread=thread, content="test", parent_message=first_message)
        third_message.save()

        fourth_message = Message(thread=thread, content="test", parent_message=second_message)
        fourth_message.save()

        fifth_message = Message(thread=thread, content="test", parent_message=fourth_message)
        fifth_message.save()

        all_replies = first_message.all_replies()
        self.assertEquals(all_replies, {
            first_message: [
                {
                    second_message: [
                        {
                            fourth_message: [
                                {fifth_message: []}
                            ]
                        }
                    ]
                },
                {
                    third_message: []
                }
            ]
        })