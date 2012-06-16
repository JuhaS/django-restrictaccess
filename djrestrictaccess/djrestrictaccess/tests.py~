"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test import Client
from django.http import HttpRequest
from django.http import HttpResponse
from djrestrictaccess.models import *
from djrestrictaccess.restrictaccessciddleware import RestrictAccessMiddleware
import datetime
from django.utils import timezone

class MockupSession:
    session_key="1111111111"

class SimpleTest(TestCase):
    
    def _get_request(self, path):
        request = HttpRequest()
        request.META = {
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': 8000,
        }
        request.path = request.path_info = path
        request.session = MockupSession()
        return request

    def setUp(self):
        pass
    
    def tearDown(self):
        for k in AccessKey.objects.all():
            k.delete()
        for k in WhitelistedSession.objects.all():
            k.delete()    

    def test_correct_key(self):
        AccessKey.objects.create(key="12345678901234567890", accessesLeft=1)
        request = self._get_request('/unlock?key=12345678901234567890')
        resp = RestrictAccessMiddleware().process_request(request)
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(resp._get_content().find(RestrictAccessMiddleware().PROTECTED_ACCESS_GRANTED.split('{')[0]), -1)

    def test_incorrect_key(self):
        AccessKey.objects.create(key="12345678901234567890", accessesLeft=1)
        request = self._get_request('/unlock?key=12345111111234567111')
        resp = RestrictAccessMiddleware().process_request(request)
        self.assertNotEqual(resp, None)
        self.assertEqual(resp.status_code, 403)
        self.assertNotEqual(resp._get_content().find(RestrictAccessMiddleware().PROTECTED_INCORRECT_KEY), -1)
    
    def test_unauthorized_no_session(self):
        AccessKey.objects.create(key="12345678901234567890", accessesLeft=1)
        WhitelistedSession.objects.create(sessionkey="111122222", expiry=datetime.datetime.now().replace(tzinfo=timezone.utc)+datetime.timedelta(hours=1))
        request = self._get_request('/normalsite')
        resp = RestrictAccessMiddleware().process_request(request)
        self.assertNotEqual(resp, None)
        self.assertEqual(resp.status_code, 403)
        self.assertNotEqual(resp._get_content().find(RestrictAccessMiddleware().PROTECTED_SITE_NOT_PUBLIC_MSG), -1)

    def test_authorized(self):
        WhitelistedSession.objects.create(sessionkey="1111111111", expiry=datetime.datetime.now().replace(tzinfo=timezone.utc)+datetime.timedelta(hours=1))
        request = self._get_request('/normalsite')        
        resp = RestrictAccessMiddleware().process_request(request)
        self.assertEqual(resp, None)

    def test_authorized_accesspage(self):
        WhitelistedSession.objects.create(sessionkey="1111111111", expiry=datetime.datetime.now().replace(tzinfo=timezone.utc)+datetime.timedelta(hours=1))
        request = self._get_request('/unlock?key=22222222221111111111')        
        resp = RestrictAccessMiddleware().process_request(request)
        self.assertNotEqual(resp, None)
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(resp._get_content().find(RestrictAccessMiddleware().PROTECTED_ACCESS_GRANTED_ALREADY), -1)



    def test_access_decrease(self):
        a = AccessKey.objects.create(key='22222222222222222222', accessesLeft=2)
        request = self._get_request('/unlock?key=22222222222222222222')
        request.session.sessionkey='2222222222'
        resp = RestrictAccessMiddleware().process_request(request)
        acc = AccessKey.objects.get(key='22222222222222222222')
        self.assertEqual(acc.accessesLeft, 1)

    def test_access_last(self):
        AccessKey.objects.create(key='33333333333333333333', accessesLeft=1)
        request = self._get_request('/unlock?key=33333333333333333333')
        request.session.sessionkey='3333333333'
        resp = RestrictAccessMiddleware().process_request(request)
        
        try:
            AccessKey.objects.get(key='33333333333333333333')
            self.assertFalse(True, "AccessKey should be deleted.")
        except AccessKey.DoesNotExist:
            pass

    def test_admin_unauthorized(self):
        with self.settings(PROTECTED_ADMIN_KEY='99999999998888888888'):
            request = self._get_request('/protect_admin?admin_key=22222111112222211111')
            request.session.sessionkey='3333333333'
            resp = RestrictAccessMiddleware().process_request(request)
            self.assertNotEqual(resp._get_content().find(RestrictAccessMiddleware().PROTECTED_INCORRECT_ADMIN_KEY), -1)

    def test_admin_correct_key(self):
        with self.settings(PROTECTED_ADMIN_KEY='99999999998888888888'):
            request = self._get_request('/protect_admin?admin_key=99999999998888888888')
            request.META['HTTP_HOST']="localhost:8000"
            request.session.sessionkey='3333333333'
            resp = RestrictAccessMiddleware().process_request(request)
            self.assertNotEqual(resp._get_content().find(RestrictAccessMiddleware().PROTECTED_NEW_ACCESSKEY_CREATED.split('{')[0]), -1)

    def test_no_session(self):
        AccessKey.objects.create(key="12345678901234567890", accessesLeft=1)
        request = self._get_request('/any')
        request.session = None
        resp = RestrictAccessMiddleware().process_request(request)
        self.assertNotEqual(resp, None)
        self.assertEqual(resp.status_code, 500)
        self.assertNotEqual(resp._get_content().find(RestrictAccessMiddleware().PROTECTED_NO_SESSION), -1)
           

