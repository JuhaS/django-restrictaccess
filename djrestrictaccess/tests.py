"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
"""

from django.test import TestCase
from django.http import HttpRequest
from djrestrictaccess.models import *
from djrestrictaccess.restrictaccessmiddleware import RestrictAccessMiddleware
from django.utils import timezone
import datetime
import random
import string


class MockupSession:
    session_key = "1111111111"


class SimpleTest(TestCase):

    def _create_request(self, path):
        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': 8000,
        }
        request.path = request.path_info = path
        request.session = MockupSession()
        return request

    def _assertContains(self, resp, message):
        '''
        Asserts that given response contains the given message. Response content
        is a template so the message should occur as template tag (eg {TEST_MSG}).
        '''
        self.assertNotEqual(resp._get_content().find(message.split('{')[0]), -1)

    def _createRandomAccessKey(self, accessesLeft=1, id=None):
        '''
        Creates an AccessKey and inserts it into the database. If no id is given a
        random id is generated.
        '''
        if id and len(id) is not 20:
            assertFalse(True, "Length of id should be 20")
        if not id:
            idStr = "".join(random.choice(string.digits) for x in range(20))
        else:
            if len(id) is not 20:
                assertFalse(True, "Length of id should be 20")
            idStr = id
        AccessKey.objects.create(key=idStr, accessesLeft=accessesLeft)
        return idStr

    def setUp(self):
        self.mw = RestrictAccessMiddleware()
        pass

    def tearDown(self):
        for k in AccessKey.objects.all():
            k.delete()
        for k in WhitelistedSession.objects.all():
            k.delete()

    def test_correct_key(self):
        # setup
        id = self._createRandomAccessKey()
        request = self._create_request('/unlock?key=' + id)
        # process
        resp = self.mw.process_request(request)
        # validate
        self.assertEqual(resp.status_code, 200)
        self._assertContains(resp, self.mw.PROTECTED_ACCESS_GRANTED)

    def test_incorrect_key(self):
        # setup
        id = self._createRandomAccessKey()
        request = self._create_request('/unlock?key=' + id[:-6] + "111111")
        # process
        resp = self.mw.process_request(request)
        # validate
        self.assertNotEqual(resp, None)
        self.assertEqual(resp.status_code, 403)
        self._assertContains(resp, self.mw.PROTECTED_INCORRECT_KEY)

    def test_unauthorized_no_session(self):
        # setup
        self._createRandomAccessKey()
        WhitelistedSession.objects.create(sessionkey="111122222", expiry=datetime.datetime.now().replace(tzinfo=timezone.utc) + datetime.timedelta(hours=1))
        request = self._create_request('/normalsite')
        # process
        resp = self.mw.process_request(request)
        # validate
        self.assertNotEqual(resp, None)
        self.assertEqual(resp.status_code, 403)
        self._assertContains(resp, self.mw.PROTECTED_SITE_NOT_PUBLIC_MSG)

    def test_authorized(self):
        # setup
        WhitelistedSession.objects.create(sessionkey="1111111111", expiry=datetime.datetime.now().replace(tzinfo=timezone.utc) + datetime.timedelta(hours=1))
        request = self._create_request('/normalsite')
        # process
        resp = self.mw.process_request(request)
        # validate
        self.assertEqual(resp, None)

    def test_authorized_accesspage(self):
        # setup
        WhitelistedSession.objects.create(sessionkey="1111111111", expiry=datetime.datetime.now().replace(tzinfo=timezone.utc) + datetime.timedelta(hours=1))
        request = self._create_request('/unlock?key=22222222221111111111')
        # process
        resp = self.mw.process_request(request)
        # validate
        self.assertNotEqual(resp, None)
        self.assertEqual(resp.status_code, 200)
        self._assertContains(resp, self.mw.PROTECTED_ACCESS_GRANTED_ALREADY)

    def test_access_decrease(self):
        # setup
        id = self._createRandomAccessKey(accessesLeft=2)
        request = self._create_request('/unlock?key=' + id)
        request.session.sessionkey = '2222222222'
        # process
        self.mw.process_request(request)
        # validate
        acc = AccessKey.objects.get(key=id)
        self.assertEqual(acc.accessesLeft, 1)

    def test_access_last(self):
        # setup
        id = self._createRandomAccessKey(accessesLeft=1)
        request = self._create_request('/unlock?key=' + id)
        request.session.sessionkey = '3333333333'
        # process
        self.mw.process_request(request)
        # validate
        try:
            AccessKey.objects.get(key=id)
            self.assertFalse(True, "AccessKey should be deleted.")
        except AccessKey.DoesNotExist:
            pass

    def test_admin_unauthorized(self):
        # setup
        with self.settings(PROTECTED_ADMIN_KEY='99999999998888888888'):
            request = self._create_request('/protect_admin?admin_key=22222111112222211111')
            request.session.sessionkey = '3333333333'
            # process
            resp = self.mw.process_request(request)
            # validate
            self._assertContains(resp, self.mw.PROTECTED_INCORRECT_ADMIN_KEY)

    def test_admin_correct_key(self):
        # setup
        with self.settings(PROTECTED_ADMIN_KEY='99999999998888888888'):
            request = self._create_request('/protect_admin?admin_key=99999999998888888888')
            request.META['HTTP_HOST'] = "localhost:8000"
            request.session.sessionkey = '3333333333'
            # process
            resp = self.mw.process_request(request)
            # validate
            self._assertContains(resp, self.mw.PROTECTED_NEW_ACCESSKEY_CREATED)

    def test_no_session(self):
        # setup
        self._createRandomAccessKey(accessesLeft=1)
        request = self._create_request('/any')
        request.session = None
        # process
        resp = self.mw.process_request(request)
        # validate
        self.assertNotEqual(resp, None)
        self.assertEqual(resp.status_code, 500)
        self._assertContains(resp, self.mw.PROTECTED_NO_SESSION)
