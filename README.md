django-restrictaccess
=====================

Django library that allows to restrict access (user needs a key) to any django site in a plug-n-play fashion. You won't need to change any of your current url conf's or user management, this works completely on the middleware layer.

Version  0.1, use with caution. It does include tests.

Features
-------------

 * Block your site from anyone who doesn't have correct access url.
 * Once access url is used, current users session allows access access for 1 hour (configurable). Same acess url can be used 2 times (configurable). Access url looks like: ```http://yourhost.com/unlock?key=12345123451234512345```.
 * Admin url that allows you to create access url's just by opening an url. You define the admin password in settings.py. Admin url looks like: ```http://yourhost.com/protect_admin?key=YOURSECRETPASS```
 * This is not 100% security solution, but probably sufficient for showing your prototypes to friends or alpha testing your site.


Installation
-------------

 * Install with pip from this repository: ```pip install -e git+git://github.com/JuhaS/django-restrictaccess.git#egg=djrestrictaccess```
 * 
 * In settings.py add ```djrestrictaccess``` to ```INSTALLED_APPS``` (needed for the models)
 * In settings.py add ```djrestrictaccess.restrictaccessmoddleware.RestrictAccessMiddleware``` to end of MIDDLEWARE_CLASSES.
 * In settings.py add variable ```PROTECTED_ADMIN_KEY``` that is 20 characters as your admin password. For example ```PROTECTED_ADMIN_KEY = "99999999998888888888" ```
 * Run ```python manage.py syncdb```.
 
If you did the points above your site should be blocked from visitors who don't have the access url given by you.


Usage
-------------

 * Go to ```http://yourhost.com/protect_admin?admin_key=_YOUR_20_CHAR_KEY_``` where you replace _YOUR_20_CHAR_KEY_ with the key you set in settings.py. Every time you open this url you get one new access url that can be used to access the site.
 * Access url looks like:  ```http://yoursite.com/unlock?key=99999999991111111111``` that gives anyone that uses it 60min access to site for 2 times.

Configuration
-------------

You can configure many error and status messages by assigning variables in settings.py (for example ```PROTECTED_SITE_NOT_PUBLIC_MSG = "Not allowed"```. Check protectmiddlewareapp/protectmiddleware.py to see all configurable variables.

Configurable variables (override them in settings.py):
* PROTECTED_NEW_ACCESSKEY_VALID_TIMES, default=2
* PROTECTED_EXPIRY_HOURS, default=1
* PROTECTED_SITE_NOT_PUBLIC_MSG, 'Site is not public. You need special url to get access.'
* PROTECTED_ACCESS_GRANTED, default='You have access for {expiry_hours} hours on this session. You have {sessions_left} sessions left for your access url. Click <a href="/">HERE</a> to get to landing page.'
* PROTECTED_NEW_ACCESSKEY_CREATED, default='New Access Key created successfully. This url gives access {access_times} times for {access_hours} hours each. Give this url to anyone who you wish to give access to: <div id="createdUrl">{created_url}</div>'
* PROTECTED_ACCESS_GRANTED_ALREADY, default=You have already been granted access. Click <a href="/">HERE</a> to get to landing page.'
* PROTECTED_ACCESS_EXPIRED, default='Your access time ran out.'
* PROTECTED_NO_SESSION, default='Session not detected. Is the SessionMiddleware in the configuration.'
* PROTECTED_INCORRECT_KEY, default='Invalid key'
* PROTECTED_INCORRECT_ADMIN_KEY, 'default=Invalid admin key'