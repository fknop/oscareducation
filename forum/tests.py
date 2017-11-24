# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, Client, RequestFactory

from forum.views import forum_dashboard, thread as get_thread
from promotions.models import Lesson, Stage
from users.models import Professor, Student
from skills.models import Skill
from .models import Thread, Message
from .views import deepValidateAndFetch
from dashboard import private_threads, public_class_threads, public_teacher_threads_student, get_thread_set
from views import create_thread, reply_thread

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium_intro.selenium_tests.test import SeleniumTestCase
from selenium_intro.selenium_tests.webdriver import CustomWebDriver
from selenium.common.exceptions import NoSuchElementException
from django.core.urlresolvers import reverse

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

    def test_reply_parent_message(self):
        content = 'content of the new message'
        response = self.c.post('/forum/thread/{}'.format(self.thread_id), data={'content': content})

        messages = Message.objects.all().filter(thread=self.thread_lesson)

        self.assertEquals(messages.last().content, content)
        self.assertEquals(response.status_code, 302)  # 302 because redirects

        content = 'content'
        response = self.c.post('/forum/thread/{}?reply_to={}'.format(self.thread_id, messages.last().id), data={'content': content})
        self.assertEquals(response.status_code, 302)


    def test_reply_unknown_parent_message(self):
        content = 'content'
        response = self.c.post('/forum/thread/{}?reply_to=155'.format(self.thread_id), data={'content': content})
        self.assertEquals(response.status_code, 404)


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
            "skills": "422230 422231",
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
            "skills": "422230 422231",
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
            "skills": "422230 422231",
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
            "skills": "l m",
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
            "skills": "422230 422231",
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
            "skills": "422230 422231",
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

class SeleniumTestCase(StaticLiveServerTestCase):
    """
    A base test case for selenium, providing hepler methods for generating
    clients and logging in profiles.
    """
        
    def open(self, url):
        self.wd.get("%s%s" % (self.live_server_url, url))

class Auth(SeleniumTestCase):

    def setUp(self):
        # setUp is where you setup call fixture creation scripts
        # and instantiate the WebDriver, which in turns loads up the browser.
        User.objects.create_superuser(username='admin',
                                      password='pw',
                                      email='info@lincolnloop.com')

        # Instantiating the WebDriver will load your browser
        self.wd = CustomWebDriver()

    def tearDown(self):
        # Don't forget to call quit on your webdriver, so that
        # the browser is closed after the tests are ran
        self.wd.quit()

    # Just like Django tests, any method that is a Selenium test should
    # start with the "test_" prefix.
    def test_login(self):
        """
        Django Admin login test
        """
        # Open the admin index page
        self.open(reverse('admin:index'))

        # Selenium knows it has to wait for page loads (except for AJAX requests)
        # so we don't need to do anything about that, and can just
        # call find_css. Since we can chain methods, we can
        # call the built-in send_keys method right away to change the
        # value of the field
        self.wd.find_css('#id_username').send_keys("admin")
        # for the password, we can now just call find_css since we know the page
        # has been rendered
        self.wd.find_css("#id_password").send_keys('pw')
        # You're not limited to CSS selectors only, check
        # http://seleniumhq.org/docs/03_webdriver.html for
        # a more compreehensive documentation.
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        # Again, after submiting the form, we'll use the find_css helper
        # method and pass as a CSS selector, an id that will only exist
        # on the index page and not the login page
        self.wd.find_css("#content-main")
        
class SeleniumDashboardTest(SeleniumTestCase):

    def setUp(self):
        
        self.user = User(username="Brandon")
        self.user.save()
        self.second_user = User(username="Kevin")
        self.second_user.save()
        self.teacher_user = User(username="Vince")
        self.teacher_user.set_password('12345')
        self.teacher_user.save()
        self.second_teacher_user = User(username="Nicolas")
        self.second_teacher_user.save()

        self.student = Student(user=self.user)
        self.student.save()
        self.second_student = Student(user=self.second_user)
        self.second_student.save()
        self.teacher = Professor(user=self.teacher_user, is_pending=False)
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

        # Instantiating the WebDriver will load your browser
        self.wd = CustomWebDriver()

    def tearDown(self):
        self.wd.quit()
    def test_login(self):
        
        self.wd.get(self.live_server_url)

        
        #time.sleep(3)
        self.wd.find_element_by_xpath('//a[@href="/accounts/usernamelogin/"]').click()
        #time.sleep(3)
        self.wd.get(self.live_server_url + '/accounts/usernamelogin/')
        #time.sleep(3)
        self.wd.find_element_by_id('id_username').send_keys("Vince")
        #time.sleep(2)
        
        
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(2)
        self.wd.find_element_by_id("id_password").send_keys('12345')
        #time.sleep(2)
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(2) 
        self.wd.find_element_by_link_text('English')
        #time.sleep(2)
        self.wd.find_element_by_link_text('French')
        #time.sleep(2)
        self.wd.get(self.live_server_url + '/forum/')
        #html body div.fond div.container.centralcontainer div.container-fluid.boxclasseTitle div.center table.table.table-hover tbody tr#42.thread td p.title
        #Information regarding w/e
        #<p class="title">Information regarding w/e</p>
        ##\34 2 > td:nth-child(1) > p:nth-child(1)
        #time.sleep(2)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'Help')]]")
        #time.sleep(2)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'Send help')]]")
        #time.sleep(2)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'Information regarding w/e')]]")
        #time.sleep(2)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'Information regarding spam')]]")
        #time.sleep(2)

class Scenario2Test(SeleniumTestCase):

    def setUp(self):
        
        self.user = User(username="Bob")
        self.user.set_password('12345')
        self.user.save()
        self.second_user = User(username="Kevin")
        self.second_user.save()
        self.teacher_user = User(username="Vince")
        self.teacher_user.set_password('12345')
        self.teacher_user.save()
        self.second_teacher_user = User(username="Nicolas")
        self.second_teacher_user.save()

        self.student = Student(user=self.user, is_pending=False)
        self.student.save()
        self.second_student = Student(user=self.second_user)
        self.second_student.save()
        self.teacher = Professor(user=self.teacher_user, is_pending=False)
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

        self.thread = Thread(title="Bob, replytothis", author=self.user, recipient=self.teacher_user)
        self.thread.save()

        self.second_thread = Thread(title="Send help", author=self.second_user, lesson=self.second_lesson)
        self.second_thread.save()

        self.third_thread = Thread(title="Information regarding w/e", author=self.teacher_user, professor=self.teacher)
        self.third_thread.save()

        self.fourth_thread = Thread(title="Information regarding spam", author=self.teacher_user,
                                    professor=self.teacher)
        self.fourth_thread.save()

        # Instantiating the WebDriver will load your browser
        self.wd = CustomWebDriver()

    def tearDown(self):
        self.wd.quit()
    def test_login(self):
        
        self.wd.get(self.live_server_url)
        time.sleep(1)
        self.wd.get(self.live_server_url + '/accounts/usernamelogin/')
        #time.sleep(3)
        time.sleep(1)
        self.wd.find_element_by_id('id_username').send_keys("Bob")
        #time.sleep(2)
        time.sleep(1)
        
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(2)
        time.sleep(1)
        self.wd.find_element_by_id("id_password").send_keys('12345')
        #time.sleep(2)
        time.sleep(1)
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(2)
        time.sleep(1)
        self.wd.get(self.live_server_url + '/forum/')
        time.sleep(1)
        #html body div.fond div.container.centralcontainer div.container-fluid.boxclasseTitle div.center table.table.table-hover tbody tr#42.thread td p.title
        #Information regarding w/e
        #<p class="title">Information regarding w/e</p>
        ##\34 2 > td:nth-child(1) > p:nth-child(1)
        #time.sleep(2)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'Bob, replytothis')]]").click()
        time.sleep(1)
        self.wd.find_element_by_xpath('//textarea[@class="form-control"]').send_keys("this is not a reply")
        time.sleep(1)
        self.wd.find_element_by_xpath('//button[@id="btn"]').click()
        time.sleep(2)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'this is not a reply')]]")
        time.sleep(1)
        
        #time.sleep(2)
class Scenario1Test(SeleniumTestCase):

    def setUp(self):
        
        self.user = User(username="Bob")
        self.user.set_password('12345')
        self.user.save()
        self.second_user = User(username="Alice")
        self.second_user.set_password('12345')
        self.second_user.save()
        self.teacher_user = User(username="John")
        self.teacher_user.set_password('12345')
        self.teacher_user.save()
        self.second_teacher_user = User(username="Nicolas")
        self.second_teacher_user.save()

        self.student = Student(user=self.user, is_pending=False)
        self.student.save()
        self.second_student = Student(user=self.second_user, is_pending=False)
        self.second_student.save()
        self.teacher = Professor(user=self.teacher_user, is_pending=False)
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

        self.thread = Thread(title="Bob, replytothis", author=self.user, recipient=self.teacher_user)
        self.thread.save()

        self.second_thread = Thread(title="Send help", author=self.second_user, lesson=self.second_lesson)
        self.second_thread.save()

        self.third_thread = Thread(title="Information regarding w/e", author=self.teacher_user, professor=self.teacher)
        self.third_thread.save()

        self.fourth_thread = Thread(title="Information regarding spam", author=self.teacher_user,
                                    professor=self.teacher)
        self.skill1 = Skill(code=422230, name="Compter deux par deux", description="")
        self.skill1.save()
        self.skill2 = Skill(code=422231, name="Lacer ses chaussures", description="")
        self.skill2.save()
        self.fourth_thread.save()

        # Instantiating the WebDriver will load your browser
        self.wd = CustomWebDriver()

    def tearDown(self):
        self.wd.quit()
    def test_login(self):
        
        self.wd.get(self.live_server_url)
        #time.sleep(3)
        self.wd.get(self.live_server_url + '/accounts/usernamelogin/')
        #time.sleep(3)
        time.sleep(1)
        self.wd.find_element_by_id('id_username').send_keys("Bob")
        #time.sleep(2)
        time.sleep(1)
        
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(2)
        time.sleep(1)
        self.wd.find_element_by_id("id_password").send_keys('12345')
        #time.sleep(2)
        time.sleep(1)
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(2)
        time.sleep(1)
        self.wd.get(self.live_server_url + '/forum/write/')
        #time.sleep(2)
        time.sleep(1)
        self.wd.find_element_by_xpath('//input[@name="title"]').send_keys("J ai une question mr John")
        self.wd.find_element_by_xpath('//input[@value="private"]').click()
        self.wd.find_element_by_xpath('//input[@name="visibdata"]').send_keys(str(self.teacher_user.id))
        self.wd.find_element_by_xpath('//input[@name="skills"]').send_keys(str(422230))
        self.wd.find_element_by_xpath('//textarea[@name="content"]').send_keys("je suis nul en Calcul, please Help")
        time.sleep(1)
        self.wd.find_element_by_xpath('//button[@type="submit"]').click()
        time.sleep(1)
        self.wd.get(self.live_server_url + '/accounts/logout/')
        self.wd.get(self.live_server_url + '/accounts/usernamelogin/')
        self.wd.find_element_by_id('id_username').send_keys("John")
        #time.sleep(2)
        time.sleep(1)
        
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(2)
        time.sleep(1)
        self.wd.find_element_by_id("id_password").send_keys('12345')
        #time.sleep(2)
        time.sleep(1)
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        
        self.wd.get(self.live_server_url + '/forum/')
        self.wd.find_element_by_xpath("//*[text()[contains(., 'J ai une question mr John')]]").click()
        time.sleep(1)
        self.wd.find_element_by_xpath('//textarea[@class="form-control"]').send_keys("Tu es trop nul en Math, rien à faire")
        self.wd.find_element_by_xpath('//button[@id="btn"]').click()
        time.sleep(2)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'Tu es trop nul en Math, rien à faire')]]")
        time.sleep(1)
        self.wd.get(self.live_server_url + '/accounts/logout/')
        self.wd.get(self.live_server_url + '/accounts/usernamelogin/')
        self.wd.find_element_by_id('id_username').send_keys("Alice")
        #time.sleep(2)
        
        
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(2)
        self.wd.find_element_by_id("id_password").send_keys('12345')
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        time.sleep(1)
        self.wd.get(self.live_server_url + '/forum/')
        with self.assertRaises(NoSuchElementException):
            self.wd.find_element_by_xpath("//*[text()[contains(., 'J ai une question mr John')]]")
        
        
        #time.sleep(2)
