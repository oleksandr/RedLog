# -*- coding: utf-8 -*-

from distutils.core import setup
import platform

if platform.system() == 'Windows':
    import py2exe

files = ["images/*", "resources/*"]

setup(name = "RedLog",
    version = "0.1",
    description = "Redmine time tracking application written using Qt/PyQt",
    author = "Postindustria",
    author_email = "alexander.lobunets@postindustria.com",
    url = "http://www.postindustria.com",
    packages = ['redlog', 'redlog.ui', 'redlog.redmine'],
    package_data = {'package' : files },
    scripts = ["redlogapp"],
	windows=[{"script":"redlog\main.py"}], 
	options={"py2exe":{"includes":["sip", "pyparsing"]}},
    long_description = """Redmine time tracking application written using Qt/PyQt.""" 
) 