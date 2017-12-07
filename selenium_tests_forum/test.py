# -*- coding: utf-8 -*-
from __future__ import unicode_literals



from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, Client, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile

import json
import time
import os

from django.utils.timezone import utc
from forum.views import forum_dashboard, thread as get_thread, get_skills, get_resources_list

from promotions.models import Lesson, Stage
from users.models import Professor, Student
from skills.models import Skill, Section
from resources.models import Resource
from forum.models import Thread, Message, MessageAttachment
from forum.views import deepValidateAndFetch
from forum.dashboard import private_threads, public_class_threads, public_teacher_threads_student, get_thread_set
from forum.views import create_thread, reply_thread

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium_intro.selenium_tests.test import SeleniumTestCase
from selenium_intro.selenium_tests.webdriver import CustomWebDriver
from selenium.common.exceptions import NoSuchElementException
from django.core.urlresolvers import reverse
from selenium.webdriver.common.action_chains import ActionChains

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

    def test_dashboard(self):
        
        self.wd.get(self.live_server_url)

        time.sleep(1)
        self.wd.get(self.live_server_url + '/accounts/usernamelogin/')
        time.sleep(1)
        self.wd.find_element_by_id('id_username').send_keys("Vince")
        time.sleep(1)
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        time.sleep(1)
        self.wd.find_element_by_id("id_password").send_keys('12345')
        time.sleep(1)
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        time.sleep(1) 
        self.wd.find_element_by_link_text('English')
        time.sleep(1)
        self.wd.find_element_by_link_text('French')
        time.sleep(1)
        self.wd.get(self.live_server_url + '/forum')
        time.sleep(1)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'Help')]]")
        time.sleep(1)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'Send help')]]")
        time.sleep(1)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'Information regarding w/e')]]")
        time.sleep(1)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'Information regarding spam')]]")
        time.sleep(1)
        

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


        self.thread = Thread(title="Bob, réponds avec un message", author=self.user, recipient=self.teacher_user)
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

    def test_a_post_a_reply(self):
        
        self.wd.get(self.live_server_url)
        time.sleep(1)
        self.wd.get(self.live_server_url + '/accounts/usernamelogin/')
        #time.sleep(1)
        time.sleep(1)
        self.wd.find_element_by_id('id_username').send_keys("Bob")
        #time.sleep(1)
        time.sleep(1)
        
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(1)
        time.sleep(1)
        self.wd.find_element_by_id("id_password").send_keys('12345')
        #time.sleep(1)
        time.sleep(1)
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(1)
        time.sleep(1)
        self.wd.get(self.live_server_url + '/forum/')
        time.sleep(1)
        time.sleep(1)
        #html body div.fond div.container.centralcontainer div.container-fluid.boxclasseTitle div.center table.table.table-hover tbody tr#42.thread td p.title
        #Information regarding w/e
        #<p class="title">Information regarding w/e</p>
        ##\34 2 > td:nth-child(1) > p:nth-child(1)
        #time.sleep(1)

        self.wd.find_element_by_xpath("//*[text()[contains(., 'Bob, réponds avec un message')]]").click()
        time.sleep(1)
        self.wd.find_element_by_xpath('//textarea[@class="form-control"]').send_keys("ceci est un messsssage")
        time.sleep(1)
        self.wd.find_element_by_xpath('//button[@id="reply-btn"]').click()
        time.sleep(1)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'ceci est un messsssage')]]")
        time.sleep(1)
        self.wd.find_element_by_xpath('//i[@class="fa fa-edit"]').click()
        time.sleep(1)
        self.wd.find_element_by_xpath('//textarea[@id="edit-textarea"]').clear()
        time.sleep(1)
        self.wd.find_element_by_xpath('//textarea[@id="edit-textarea"]').send_keys("ceci est un message")
        time.sleep(1)
        self.wd.find_element_by_xpath('//button[@id="edit-confirm"]').click()
        time.sleep(1)
        self.wd.find_element_by_xpath('//textarea[@class="form-control"]').send_keys("cedi est un message inutile que je vais supprimer")
        time.sleep(1)
        self.wd.find_element_by_xpath('//button[@id="reply-btn"]').click()
        time.sleep(1)
        self.wd.find_elements_by_xpath('//button[@class="delete-btn"]')[1].click()
        time.sleep(1)
        
        
        self.wd.get(self.live_server_url + '/accounts/logout/')
        self.wd.get(self.live_server_url + '/accounts/usernamelogin/')
        self.wd.find_element_by_id('id_username').send_keys("Vince")
        #time.sleep(1)
        
        
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(1)
        self.wd.find_element_by_id("id_password").send_keys('12345')
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        self.wd.get(self.live_server_url + '/forum/')
        time.sleep(1)
        self.wd.find_element_by_xpath('//input[@id="search"]').send_keys("Bob, réponds avec un message")
        time.sleep(1)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'Bob, réponds avec un message')]]").click()
        time.sleep(1)
        self.wd.find_element_by_xpath('//i[@class="fa fa-reply reply-btn"]').click()
        time.sleep(1)
        self.wd.find_element_by_xpath('//textarea[@id="content"]').send_keys("Je te réponds bob")
        time.sleep(1)
        self.wd.find_element_by_xpath('//button[@id="reply-btn"]').click()
        time.sleep(1)
        self.wd.find_elements_by_xpath('//i[@class="fa fa-reply reply-btn"]')[1].click()
        time.sleep(1)
        self.wd.find_element_by_xpath('//textarea[@id="content"]').send_keys("Je me réponds à moi même")
        time.sleep(1)
        self.wd.find_element_by_xpath('//button[@id="reply-btn"]').click()
        time.sleep(1)
        self.wd.find_element_by_xpath('//button[@class="delete-btn"]').click()
        time.sleep(1)
        
        self.wd.get(self.live_server_url + '/accounts/logout/')
        self.wd.get(self.live_server_url + '/accounts/usernamelogin/')
        self.wd.find_element_by_id('id_username').send_keys("Bob")
        #time.sleep(1)
        
        
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(1)
        self.wd.find_element_by_id("id_password").send_keys('12345')
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        self.wd.get(self.live_server_url + '/forum/')
        time.sleep(1)
        self.wd.find_element_by_xpath('//a[@id="bellicon"]').click()
        time.sleep(1)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'Forum: nouveau message')]]").click()
        time.sleep(1)
        self.wd.find_elements_by_xpath('//i[@class="fa fa-reply reply-btn"]')[1].click()
        time.sleep(1)
        self.wd.find_element_by_xpath('//textarea[@id="content"]').send_keys("Merci de m'avoir répondu")
        time.sleep(1)
        self.wd.find_element_by_xpath('//button[@id="reply-btn"]').click()
        time.sleep(1)
        
        #time.sleep(1)
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


        self.lesson = Lesson(id=1, name="Trigonométrie", stage_id=1)

        self.lesson.save()
        self.lesson.students.add(self.student)
        self.lesson.students.add(self.second_student)
        self.lesson.professors.add(self.teacher)
        self.lesson.save()
        self.second_lesson = Lesson(id=2, name="Analyse", stage_id=2)
        self.second_lesson.save()
        self.second_lesson.students.add(self.second_student)
        self.second_lesson.professors.add(self.teacher)
        self.second_lesson.save()


        self.thread = Thread(title="Problèmes avec les équations du premier degré", author=self.user, recipient=self.teacher_user)
        self.thread.save()

        self.second_thread = Thread(title="Aidez moi", author=self.second_user, lesson=self.second_lesson)
        self.thread = Thread(title="Bob, replytothis", author=self.user, recipient=self.teacher_user)
        self.thread.save()

        self.second_thread = Thread(title="Send help", author=self.second_user, lesson=self.second_lesson)

        self.second_thread.save()

        self.third_thread = Thread(title="Information regarding w/e", author=self.teacher_user, professor=self.teacher)
        self.third_thread.save()
        self.skill1 = Skill(code=422230, name="Compter deux par deux", description="")
        self.skill1.save()
        self.skill2 = Skill(code=422231, name="Mesurer des Angles", description="")
        self.skill2.save()
        self.fourth_thread = Thread(title="Information regarding spam", author=self.teacher_user,
                                    professor=self.teacher)
        self.stage = Stage(id=1, name="Stage1", level=1)
        self.stage.save()
        self.stage.skills.add(self.skill1)
        self.stage.skills.add(self.skill2)
        self.stage.save()
        


        self.fourth_thread = Thread(title="Information regarding spam", author=self.teacher_user,
                                    professor=self.teacher)

        # Instantiating the WebDriver will load your browser
        self.wd = CustomWebDriver()

    def tearDown(self):
        self.wd.quit()

    def test_message_public_au_prof_scenario3(self):

        self.wd.get(self.live_server_url)
        #time.sleep(1)
        self.wd.get(self.live_server_url + '/accounts/usernamelogin/')
        #time.sleep(1)
        time.sleep(1)
        self.wd.find_element_by_id('id_username').send_keys("Bob")
        #time.sleep(1)
        time.sleep(1)
        
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(1)
        time.sleep(1)
        self.wd.find_element_by_id("id_password").send_keys('12345')
        #time.sleep(1)
        time.sleep(1)
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(1)
        time.sleep(1)
        self.wd.get(self.live_server_url + '/forum/')
        time.sleep(1)
        self.wd.get(self.live_server_url + '/forum/write/')
        time.sleep(1)
        self.wd.find_element_by_xpath('//input[@name="title"]').send_keys("trigono est difficile")
        time.sleep(1)
        self.wd.find_element_by_xpath('//input[@value="public"]').click()
        time.sleep(1)
        self.wd.find_element_by_xpath('//select[@id="select-visibility"]').click()
        time.sleep(1)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'John')]]").click()
        time.sleep(1)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'Mesurer des Angles')]]").click()
        time.sleep(1)
        self.wd.find_element_by_xpath('//textarea[@name="content"]').send_keys("Monsieur John, le cours de trigono est trop dur")
        time.sleep(1)
        action=ActionChains(self.wd)
        #action.move_to_element(
        self.wd.execute_script("arguments[0].scrollIntoView();", self.wd.find_element_by_xpath('//button[@type="submit"]'))
        #).click().perform() 
        time.sleep(1)
        self.wd.find_element_by_xpath('//button[@type="submit"]').click()
        time.sleep(1)
        self.wd.get(self.live_server_url + '/accounts/logout/')
        self.wd.get(self.live_server_url + '/accounts/usernamelogin/')
        
        self.wd.find_element_by_id('id_username').send_keys("Alice")
        #time.sleep(1)
        
        
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(1)
        self.wd.find_element_by_id("id_password").send_keys('12345')
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        time.sleep(1)
        self.wd.get(self.live_server_url + '/forum/')
        time.sleep(1)
        time.sleep(1)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'trigono')]]")
        time.sleep(1)
        
        
    def test_message_aggrandi(self):
        
        self.wd.get(self.live_server_url)
        #time.sleep(1)
        self.wd.get(self.live_server_url + '/accounts/usernamelogin/')
        #time.sleep(1)
        time.sleep(1)
        self.wd.find_element_by_id('id_username').send_keys("Bob")
        #time.sleep(1)
        time.sleep(1)
        
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(1)
        time.sleep(1)
        self.wd.find_element_by_id("id_password").send_keys('12345')
        #time.sleep(1)
        time.sleep(1)
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(1)
        time.sleep(1)
        self.wd.get(self.live_server_url + '/forum/')
        time.sleep(1)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'quations')]]").click()
        time.sleep(1)
        string ='a'
        for u in range(0, 950):
            string = string + 'a \n'
        
        self.wd.find_element_by_xpath('//textarea[@class="form-control"]').send_keys(string)
        self.wd.find_element_by_xpath('//button[@id="reply-btn"]').click()
        time.sleep(1)
        path_to_file = os.path.dirname(os.path.abspath(__file__))
        my_filename = os.path.join(path_to_file, "equation.txt")
        self.wd.find_element_by_xpath('//input[@class="upload"]').send_keys(my_filename)
        time.sleep(1)
        self.wd.find_element_by_xpath('//textarea[@class="form-control"]').send_keys("ceci est un attachement")
        time.sleep(1)
        self.wd.find_element_by_xpath('//button[@id="reply-btn"]').click()
        time.sleep(1)
        self.wd.get(self.live_server_url + '/accounts/logout/')
        self.wd.get(self.live_server_url + '/accounts/usernamelogin/')
        #time.sleep(1)
        time.sleep(1)
        self.wd.find_element_by_id('id_username').send_keys("John")
        #time.sleep(1)
        time.sleep(1)
        
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(1)
        time.sleep(1)
        self.wd.find_element_by_id("id_password").send_keys('12345')
        #time.sleep(1)
        time.sleep(1)
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(1)
        time.sleep(1)
        self.wd.get(self.live_server_url + '/forum/')
        time.sleep(1)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'quations')]]").click()
        self.wd.find_element_by_xpath('//a[@class="btn btn-default btn-sm"]').click()
        
        time.sleep(1)
        
    def test_message_public_au_prof_scenario3(self):
        self.wd.get(self.live_server_url)
        #time.sleep(1)
        self.wd.get(self.live_server_url + '/accounts/usernamelogin/')
        #time.sleep(1)
        time.sleep(1)
        self.wd.find_element_by_id('id_username').send_keys("Bob")
        #time.sleep(1)
        time.sleep(1)
        
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(1)
        time.sleep(1)
        self.wd.find_element_by_id("id_password").send_keys('12345')
        #time.sleep(1)
        time.sleep(1)
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(1)
        time.sleep(1)
        self.wd.get(self.live_server_url + '/forum/')
        time.sleep(1)
        self.wd.get(self.live_server_url + '/forum/write/')
        time.sleep(1)
        self.wd.find_element_by_xpath('//input[@name="title"]').send_keys("trigono est difficile")
        time.sleep(1)
        self.wd.find_element_by_xpath('//input[@value="public"]').click()
        time.sleep(1)
        self.wd.find_element_by_xpath('//select[@id="select-visibility"]').click()
        time.sleep(1)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'John')]]").click()
        time.sleep(1)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'Mesurer des Angles')]]").click()
        time.sleep(1)
        self.wd.find_element_by_xpath('//textarea[@name="content"]').send_keys("Monsieur John, le cours de trigono est trop dur")
        time.sleep(1)
        action=ActionChains(self.wd)
        #action.move_to_element(
        self.wd.execute_script("arguments[0].scrollIntoView();", self.wd.find_element_by_xpath('//button[@type="submit"]'))
        #).click().perform() 
        time.sleep(1)
        self.wd.find_element_by_xpath('//button[@type="submit"]').click()
        time.sleep(1)
        self.wd.get(self.live_server_url + '/accounts/logout/')
        self.wd.get(self.live_server_url + '/accounts/usernamelogin/')
        
        self.wd.find_element_by_id('id_username').send_keys("Alice")
        #time.sleep(1)
        
        
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        #time.sleep(1)
        self.wd.find_element_by_id("id_password").send_keys('12345')
        self.wd.find_element_by_xpath('//input[@value="Connexion"]').click()
        time.sleep(1)
        self.wd.get(self.live_server_url + '/forum/')
        time.sleep(1)
        self.wd.find_element_by_xpath("//*[text()[contains(., 'trigono')]]")
        time.sleep(1)
        
