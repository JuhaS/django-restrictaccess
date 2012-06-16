# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='django-restrictaccess',
    version='0.0.1',
    author=u'Juha Suomalainen',
    author_email='',
    packages=['djrestrictaccess'],
    url='https://github.com/JuhaS/django-restrictaccess',
    license='BSD licence, see LICENCE.txt',
    description='Django library that allows to restrict access (user needs a key) to any django site in a plug-n-play fashion.',
    long_description=open('README.md').read(),
    zip_safe=False,
)
