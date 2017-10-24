# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.test import TestCase

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