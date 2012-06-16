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

Usage
-------------

 * Install the protectmiddlewareapp by copying the folder to somewhere in your pythonpath (pip installation coming).
 * In settings.py add protectmiddlewareapp to INSTALLED_APPS (needed for the models)
 * In settings.py add ```protectmiddlewareapp.protectmiddleware.ProtectMiddleware``` to end of MIDDLEWARE_CLASSES.
 * In settings.py add variable PROTECTED_ADMIN_KEY that is 20 characters as your admin password. For example ```PROTECTED_ADMIN_KEY = "99999999998888888888" ```
 * Run syncdb (this app includes two small models).
 
If you did the points above your site should be blocked from visitors who don't have the access url given by you.

Configuration
-------------

You can configure many error and status messages by assigning variables in settings.py (for example ```PROTECTED_SITE_NOT_PUBLIC_MSG = "Not allowed"```. Check protectmiddlewareapp/protectmiddleware.py to see all configurable variables.