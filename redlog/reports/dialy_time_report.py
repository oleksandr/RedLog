# -*- coding: utf-8 -*-
from redlog.models import LocalStore, RemoteIssuesStore
import logging
import sys
from datetime import datetime, timedelta
import time
from redlog import settings
from common import parameters_parse
import math

logging.basicConfig(level = logging.DEBUG)

def to_timedelta(number):
    number = float(number)
    hours = math.trunc(number)
    minutes = 60 * (number - hours)
    return timedelta(hours = hours, minutes = int(math.floor(minutes)))

def time_delta_str(timedelta):
    time.strftime("%H:%M", time.gmtime(timedelta.seconds)) 

def start(argv):
    day_str = parameters_parse(argv, ['day'], usage)[0]
    
    day = datetime.strptime(day_str, "%Y-%m-%d")
    
    localStore = LocalStore()
    
    credentials = localStore.get_credentials()
    if len(credentials) == 0:
        print "Can't find credentials for Redmine login. Use Redlog UI before."
        
    username = credentials[0]
    password = credentials[1]
    logging.debug('Connect to Redmine with username "%s"' % username)
    remote_store = RemoteIssuesStore(settings.REDMINE_BASE_URL, username, password)
    
    from_date = day
    to_date = day + timedelta(hours = 23, minutes = 59, seconds = 59) 
    
    logging.debug('Get time sheets between %s and %s' % (from_date, to_date))
    time_sheets = remote_store.get_time_entries(from_date, to_date)
    
    from itertools import groupby
    from operator import itemgetter

    time_sheets = sorted(time_sheets, key=itemgetter('user'))
    for user, grouper in groupby(time_sheets, key=itemgetter('user')):
        sum = timedelta()
        print u'%s' % user
        for item in grouper:
            print '  [%s] #%s %s' % (to_timedelta(item['hours']), item['issue'], item['subject'])
            sum = sum + to_timedelta(item['hours'])
        print u'  [%s]' % sum
        print u'\n'

def usage():
    print "usage: dialy_time_report.py --day=DATE"
    print "System will drop time report into console"

if __name__ == '__main__':
    start(sys.argv[1:])