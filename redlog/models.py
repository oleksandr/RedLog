# -*- coding: utf-8 -*-

import os
import sqlite3
import datetime
import re
from redlog import redmine

class RemoteIssuesStore(object):
    '''
    This is a Model class
    '''
    
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
    
    def get_issues(self):
        issues = []
        issues_feed = redmine.get_issues(self.base_url, self.username, self.password)
        for issue in issues_feed.get('items'):
            m = re.search('\s#(\d+)\s', issue.get('title'))
            issues.append({'title': issue.get('title'),
                           'issue': m.group(1),
                           'url': issue.get('links')[0].get('href')})
        return issues
    
    def submit(self, issue, hours, activity, comments):
        redmine.post_time(self.base_url, self.username, self.password, issue, hours, activity, comments)
        return True
        

class LocalStore(object):
    '''
    This is a Model class
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.homedir = os.path.join(os.path.expanduser('~'), u'.redlog')
        self.cache_file = os.path.join(self.homedir, u'cache.sqlite3')
        self.connection = None
        
        self.setup()
    
    def setup(self):
        if not os.path.isdir(self.homedir):
            os.mkdir(self.homedir)

        if not os.path.exists(self.cache_file):
            self.connection = sqlite3.connect(self.cache_file)
            c = self.connection.cursor()
            c.execute('''CREATE TABLE issues (issue TEXT, title TEXT, url TEXT, updated TEXT, spenttime REAL)''')
            c.execute('''CREATE TABLE settings (username TEXT, password TEXT)''')
            self.connection.commit()
            c.close()
        else:
            self.connection = sqlite3.connect(self.cache_file)
    
    def get_credentials(self):
        c = self.connection.cursor()
        c.execute('SELECT username, password FROM settings LIMIT 0,1')
        result = c.fetchall()
        c.close()
        if len(result) == 0:
            return result
        return result[0]
    
    def set_credentials(self, username, password):
        c = self.connection.cursor()
        c.execute('SELECT username, password FROM settings')
        result = c.fetchall()
        if len(result) == 0:
            c.execute("INSERT INTO settings (username, password) VALUES (?, ?)", (username, password,))
        else:
            c.execute("UPDATE settings SET username=?, password=?", (username, password,))
        self.connection.commit()
        c.close()
        return True
    
    def reset_credentials(self):
        c = self.connection.cursor()
        c.execute("DELETE FROM settings")
        self.connection.commit()
        c.close()
        return True
        
    def get_issues(self):
        c = self.connection.cursor()
        c.execute('SELECT issue, title, url, updated, spenttime FROM issues ORDER BY issue')
        result = c.fetchall()
        c.close()
        return result
    
    def set_issues(self, issues):
        c = self.connection.cursor()
        d = datetime.date.today()
        
        c.execute("DELETE FROM issues WHERE spenttime = 0.0")
        
        for issue in issues:
            c.execute("SELECT issue FROM issues WHERE issue LIKE '%s' LIMIT 0,1" % issue.get('issue'))
            result = c.fetchall()
            if len(result) > 0:
                continue
            c.execute("INSERT INTO issues (issue, title, url, updated, spenttime) VALUES (?, ?, ?, ?, 0.0)", (issue.get('issue'), issue.get('title'), issue.get('url'), d,))
        self.connection.commit()
        c.close()
        return True
    
    def increment_time(self, value, issue):
        c = self.connection.cursor()
        
        c.execute("SELECT spenttime FROM issues WHERE issue LIKE '%s' LIMIT 0,1" % issue)
        result = c.fetchall()
        if len(result) == 0:
            return False

        record = result[0]
        d = datetime.date.today()
        c.execute("UPDATE issues SET spenttime=%d, updated='%s' WHERE issue LIKE '%s'" % (record[0] + value, d, issue))
        self.connection.commit()
        c.close()
        return True
    
    def get_spent_time(self, issue):
        c = self.connection.cursor()
        c.execute("SELECT spenttime FROM issues WHERE issue LIKE '%s' LIMIT 0,1" % issue)
        result = c.fetchall()
        if len(result) == 0:
            return 0.0
        record = result[0]
        c.close()
        return record[0]
    
    def reset_issue(self, issue):
        c = self.connection.cursor()
        d = datetime.date.today()
        c.execute("UPDATE issues SET spenttime=0.0, updated='%s' WHERE issue LIKE '%s'" % (d, issue))
        self.connection.commit()
        c.close()
        return True

def format_lcd_time(time_in_seconds):
    tmp = divmod(time_in_seconds, 3600)
    tmp1 = divmod(tmp[1], 60)
    return u"%02.0f:%02.0f:%02.0f" % (tmp[0], tmp1[0], tmp1[1])

def cleanup_issue_title(title):
    return title.split(" - ")[1]