# -*- coding: utf-8 -*-
from redlog.models import LocalStore, RemoteIssuesStore
import logging
import sys
from datetime import datetime
from xls_exporter import XlsExporter
from redlog import settings
from common import parameters_parse

logging.basicConfig(level = logging.DEBUG)

def get_real_time_spend(remote_store, issue):
    logging.debug('Calculate real time spend for issue %s' % issue['#'])
    time_sheets = remote_store.get_time_entries_by_issue(issue['#'])
    result = 0
    for item in time_sheets:
        result = result + float(item['hours'])
    return round(result, 2)

def start(argv):
    query_id, start_date_str, export_file = parameters_parse(argv, ['query_id', "start_date", 'file'], usage)
    
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.now()
        
    localStore = LocalStore()
    logging.debug('Loading issues from local store by query_id=%s and between %s and %s' % (query_id, start_date, end_date))
    planned_issues = localStore.get_issues_by_query(query_id,
                                   start_date.strftime("%Y-%m-%d %H:%M:%S"),
                                   end_date.strftime("%Y-%m-%d %H:%M:%S"))
    
    credentials = localStore.get_credentials()
    if len(credentials) == 0:
        print "Can't find credentials for Redmine login. Use Redlog UI before."
        
    username = credentials[0]
    password = credentials[1]
    logging.debug('Connect to Redmine with username "%s"' % username)
    remote_store = RemoteIssuesStore(settings.REDMINE_BASE_URL, username, password)
    
    logging.debug('Getting issues from Redmine (query_id = %s)' % query_id)
    current_issues = remote_store.get_issues_by_query_id(query_id)
    
    import copy
    result = copy.copy(current_issues)
    #print len(current_issues)
    i = 0 
    for item in current_issues:
        i = i + 1
        #print '%s - %s' % (i, item['#'])
        #if item['#'] == u'2291':
        #    raise Exception, 'here'
        for plan in planned_issues:
            if unicode(item['#']) == unicode(plan['#']):
                result.remove(item)
    
    xls = XlsExporter()
    xls.add_issues_list(result)
    
    xls.save_to_file(export_file)
    
    logging.debug('Done')

def usage():
    print "usage: next_iteration.py --query_id=QUERY_ID --start_date=START_DATE --file=FILE_TO_EXPORT"

if __name__ == '__main__':
    start(sys.argv[1:])