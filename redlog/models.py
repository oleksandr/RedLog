# -*- coding: utf-8 -*-
import os
import sqlite3
import datetime
import re
from redlog import redmine
import csv

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
        redmine.post_time(self.base_url, self.username, self.password, issue, 
                          hours, activity, comments)
        return True
    
    def get_time_entries(self):
        time_entries = []
        time_entries_csv = redmine.get_time_entries(self.base_url, self.username, 
                                                     self.password)
        time_entries_csv = time_entries_csv.replace('\r\n', ' ')
        lines = time_entries_csv.split('\n')
        for line in lines[1:]:
            line_items_iter = csv.reader([line], delimiter=',', quotechar='"')
            line_items = line_items_iter.next()
            try:
                if len(line_items) > 1:                    
                    time_entries.append(
                                  {'date': line_items[0],
                                   'user': line_items[1],
                                   'activity': line_items[2],
                                   'project': line_items[3],
                                   'issue': line_items[4],
                                   'tracker': line_items[5],
                                   'subject': line_items[6],
                                   'hours': line_items[7],
                                   'comment': line_items[8]
                                   })
            except:
                raise Exception, "Can't parse line: '%s'. Result list is %s" % (line, line_items)
            for entry in time_entries:
                for key in entry.keys():
                    entry[key] = unicode(entry[key])
        
    
    def get_issues_by_query_id(self, query_id):
        issues = []
        issues_csv = redmine.get_issues_by_query_id(self.base_url, self.username, 
                                                     self.password, query_id)
        # The reader is hard-coded to recognise either '\r' or '\n'
        # as end-of-line, and ignores lineterminator. 
        # This behavior may change in the future.
        issues_csv = issues_csv.replace('\r\n', ' ')
        lines = issues_csv.split('\n')
        for line in lines[1:]:
            line_items_iter = csv.reader([line], delimiter=',', quotechar='"')
            line_items = line_items_iter.next()
            #a = 0
            #for m in line_items:
            #    print '%s - %s' % (a, m)
            #    a = a + 1
            try:
                if len(line_items) > 1:                    
                    issues.append(
                                  {'#': line_items[0],
                                   'status': line_items[1],
                                   'tracker': line_items[3],
                                   'priority': line_items[4],
                                   'subject': line_items[5],
                                   'assigned to': line_items[6],
                                   'estimate time': line_items[13],
                                   '% done': line_items[12]
                                   })
            except:
                raise Exception, "Can't parse line: '%s'. Result list is %s" % (line, line_items)
            for issue in issues:
                for key in issue.keys():
                    issue[key] = unicode(issue[key])
        return issues
        

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
            c.execute('''CREATE TABLE issues_by_query (query_id INTEGER,
                        issue_id INTEGER, 
                        status TEXT, tracker TEXT,
                        priority TEXT, subject TEXT,
                        assigned_to TEXT, estimate DECIMAL(10, 1),
                        done INTEGER,
                        saved DATETIME)''')
            self.connection.commit()
            c.close()
        else:
            self.connection = sqlite3.connect(self.cache_file)
            
    def get_issues_by_query(self, query_id, start_datetime, end_datetime):
        c = self.connection.cursor()
        c.execute("SELECT * FROM issues_by_query WHERE query_id = ? AND saved BETWEEN ? AND ? ORDER BY issue_id DESC", 
                  (query_id, start_datetime, end_datetime,))
        result_sql = c.fetchall()
        result = []
        c.close()
        
        for item in result_sql:
            result.append({'#': item[1],
                          'status': item[2],
                          'tracker': item[3],
                          'priority': item[4],
                          'subject': item[5],
                          'assigned to': item[6],
                          'estimate time': item[7],
                          '% done': item[8]
                        })
        return result
    
    def save_issue_by_query(self, query_id, issue_data, saved_datetime):
        c = self.connection.cursor()
        c.execute(u"""INSERT INTO issues_by_query (query_id,
                        issue_id, status, tracker,
                        priority, subject,
                        assigned_to, estimate, done, saved) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                  (query_id, issue_data['#'], issue_data['status'], issue_data['tracker'],
                            issue_data['priority'], issue_data['subject'],
                            issue_data['assigned to'], issue_data['estimate time'],
                            issue_data['% done'], saved_datetime,))
        self.connection.commit()
        c.close()
        return True
        
    def clear_issues_by_query(self, query_id):
        c = self.connection.cursor()
        c.execute("DELETE FROM issues_by_query WHERE query_id = ?", (query_id,))
        self.connection.commit()
        c.close()
        return True
    
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