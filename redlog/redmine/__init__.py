# -*- coding: utf-8 -*-

import feedparser
import StringIO
from twill import get_browser, set_output
from twill.commands import fv, submit

b = get_browser()

# IMPORTANT:
# Patch the form parser class to ensure end select tags are processed correctly
# See: http://lists.idyll.org/pipermail/twill/2008-August/000902.html

from twill.other_packages._mechanize_dist import ClientForm

form_parser_class = b._browser._factory.soup_factory._forms_factory.form_parser_class
old_end_select = form_parser_class.end_select
def end_select(self):
    result = old_end_select(self)
    self._select = None
    return result
form_parser_class.end_select = end_select

output = StringIO.StringIO()
set_output(output)

def _login(browser, base_url, username, password):
    browser.go("%s/login" % base_url)
    #browser.showforms()
    fv("2", "username", username)
    fv("2", "password", password)    
    submit('5')

def get_issues(base_url, username, password):
    b = get_browser()
    _login(b, base_url, username, password)

    b.go("%s/issues.atom?assigned_to_id=me&set_filter=1" % base_url)
    rss_str = b.get_html()

    return feedparser.parse(rss_str)

def post_time(base_url, username, password, issue, hours, activity, comments):
    _login(b, base_url, username, password)
    
    b.go("%s/issues/%s/time_entries/new" % (base_url, issue))
    fv("3", "time_entry[hours]", str(hours))
    fv("3", "time_entry[comments]", comments)
    fv("3", "time_entry[activity_id]", activity)
    submit('7')
    #b.showforms()
    
    return True
