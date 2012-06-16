from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response, redirect, \
    render
from django.template import RequestContext
from django.utils import timezone
from djrestrictaccess.models import WhitelistedSession, AccessKey
import datetime
import random
import re
import time


class RestrictAccessMiddleware(object):

    @classmethod
    def set_variable(cls, var_name, default):
        if hasattr(settings, var_name):
            setattr(cls, var_name, getattr(settings, var_name))
        else:
            setattr(cls, var_name, default)

    def __init__(self):
        self.set_variable("PROTECTED_NEW_ACCESSKEY_VALID_TIMES", 2)
        self.set_variable("PROTECTED_EXPIRY_HOURS", 1)
        self.set_variable("PROTECTED_SLEEP_TIME_MSEC", 500)
        self.set_variable("PROTECTED_SITE_NOT_PUBLIC_MSG", "Site is not public. You need special url to get access.")
        self.set_variable("PROTECTED_ACCESS_GRANTED", 'You have access for {expiry_hours} hours on this session. You have {sessions_left} sessions left for your access url. Click <a href="/">HERE</a> to get to landing page.')
        self.set_variable("PROTECTED_NEW_ACCESSKEY_CREATED", 'New Access Key created successfully. This url gives access {access_times} times for {access_hours} hours each. Give this url to anyone who you wish to give access to: <div id="createdUrl">{created_url}</div>')
        self.set_variable("PROTECTED_ACCESS_GRANTED_ALREADY", 'You have already been granted access. Click <a href="/">HERE</a> to get to landing page.')
        self.set_variable("PROTECTED_ACCESS_EXPIRED", "Your access time ran out.")
        self.set_variable("PROTECTED_NO_SESSION", "Session not detected. Is the SessionMiddleware in the configuration.")
        self.set_variable("PROTECTED_INCORRECT_KEY", "Invalid key")
        self.set_variable("PROTECTED_INCORRECT_ADMIN_KEY", "Invalid admin key")

    @staticmethod
    def update_ip_to_sessionkey(request):
        try:
            # Try to see if ip matches whitelisted sessions
            wlSession = WhitelistedSession.objects.get(ip=request.META['REMOTE_ADDR'])
            if request.session.session_key:
                # Update session key
                wlSession.ip = None
                wlSession.sessionkey = request.session.session_key
                wlSession.save()
        except:
            pass

    @classmethod
    def handle_whitelisted_session(cls, request, wlSession):
        if wlSession.expiry < datetime.datetime.now().replace(tzinfo=timezone.utc):
            # Expired, delete it
            wlSession.delete()
            return render(request, 'protect_template.html',
                            {"title": "Unauthorized",
                             "message": cls.PROTECTED_ACCESS_EXPIRED
                             },
                            status=403)
        elif cls.url_matches_getaccess(request):
            # Already active session
            return render(request, 'protect_template.html',
                            {"title": "Session Active Already",
                             "message": cls.PROTECTED_ACCESS_GRANTED_ALREADY
                            },
                            status=200)

    @staticmethod
    def url_matches_getaccess(request):
        prog = re.compile('/unlock\?key=[0-9]{20}$')
        if re.match(prog, request.get_full_path()):
            return True
        return False

    @staticmethod
    def url_matches_admin(request):
        prog = re.compile('/protect_admin\?admin_key=[0-9]{20}$')
        if re.match(prog, request.get_full_path()):
            return True
        return False

    @staticmethod
    def get_access_key(request):
        prog = re.compile('/unlock\?key=([0-9]{20})$')
        m = re.search(prog, request.get_full_path())
        return m.group(1)

    @staticmethod
    def admin_password_matches(request):
        prog = re.compile('/protect_admin\?admin_key=([0-9]{20})$')
        m = re.search(prog, request.get_full_path())
        if m.group(1) == settings.PROTECTED_ADMIN_KEY:
            return True
        else:
            return False

    @classmethod
    def handle_admin_page(cls, request):
        if cls.admin_password_matches(request):
            key = ""
            for i in range(20):
                key += str(random.randint(0, 9))
            AccessKey.objects.create(key=key, accessesLeft=cls.PROTECTED_NEW_ACCESSKEY_VALID_TIMES)
            remote = request.META['HTTP_HOST']
            return render(request, 'protect_template.html',
                            {"title": "New Access Key Created",
                             "message": cls.PROTECTED_NEW_ACCESSKEY_CREATED.format(created_url='http://' + remote + '/unlock?key=' + key,
                                                                                access_times=cls.PROTECTED_NEW_ACCESSKEY_VALID_TIMES,
                                                                                access_hours=cls.PROTECTED_EXPIRY_HOURS)
                            },
                            status=200)
        else:
            return render(request, 'protect_template.html',
                            {"title": "Unauthorized",
                             "message": cls.PROTECTED_INCORRECT_ADMIN_KEY,
                            },
                                      status=403)

    @classmethod
    def handle_get_access_page(cls, request):
        # Sleep to prevent brute forcing
        time.sleep(cls.PROTECTED_SLEEP_TIME_MSEC / 1000)

        # Clean up expired sessions every 50 accesses (avg)
        if random.randint(0, 50) == 1:
            WhitelistedSession.objects.filter("expiry" < datetime.datetime.now()).delete()

        k = cls.get_access_key(request)
        try:
            access = AccessKey.objects.get(key=k)
            # Valid key
            if access.accessesLeft < 2:
                access.accessesLeft = 0
                access.delete()
            else:
                access.accessesLeft = access.accessesLeft - 1
                access.save()
            expiry = datetime.datetime.now().replace(tzinfo=timezone.utc)
            expiry += datetime.timedelta(hours=cls.PROTECTED_EXPIRY_HOURS)
            if request.session.session_key:
                WhitelistedSession.objects.create(expiry=expiry, sessionkey=request.session.session_key)
            else:
                client_ip = request.META['REMOTE_ADDR']
                WhitelistedSession.objects.create(expiry=expiry, ip=client_ip)
            return render(request, 'protect_template.html',
                            {"title": "Access Granted",
                             "message": cls.PROTECTED_ACCESS_GRANTED.format(expiry_hours=cls.PROTECTED_EXPIRY_HOURS, sessions_left=access.accessesLeft),
                            },
                            status=200)
        except AccessKey.DoesNotExist:
            return render(request, 'protect_template.html',
                            {"title": "Unauthorized",
                             "message": cls.PROTECTED_INCORRECT_KEY,
                             },
                            status=403)

    def process_request(self, request):
        # Check if admin page is accessed
        if self.url_matches_admin(request):
            return self.handle_admin_page(request)

        # Session required, fail if id doesn't exist
        if not request.session:
            return render(request, 'protect_template.html',
                                {"title": "Error",
                                 "message": self.PROTECTED_NO_SESSION,
                                },
                                status=500)

        self.update_ip_to_sessionkey(request)

        try:
            wlSession = WhitelistedSession.objects.get(sessionkey=request.session.session_key)
            return self.handle_whitelisted_session(request, wlSession)
        except WhitelistedSession.DoesNotExist:
            # Ungranted session
            if self.url_matches_getaccess(request):
                # User trying to use access key
                return self.handle_get_access_page(request)
            else:
                return render(request, 'protect_template.html',
                              {"title": "Unauthorized",
                               "message": self.PROTECTED_SITE_NOT_PUBLIC_MSG,
                              },
                              status=403)
