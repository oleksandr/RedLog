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
    
    all_issues_query_id = 47
    logging.debug('Getting issues from Redmine (query_id = %s)' % all_issues_query_id)
    new_issues = remote_store.get_issues_by_query_id(all_issues_query_id) # 47 is all
    
    def row_handler(exporter, issue):
        # return exporter.get_default_style()
        issue['real time spend'] = '?'
        for item in new_issues:           
            if unicode(item['#']) == unicode(issue['#']):
                if item['status'] == u'Closed':
                    item['% done'] = u'100'
                    
                if item['status'] == u'Rejected':
                    item['% done'] = u'0'
                    
                issue['status'] = item['status']
                issue['assigned to'] = item['assigned to']
                issue['% done'] = item['% done']
                if unicode(item['% done']) == u'100':
                    issue['real time spend'] = get_real_time_spend(remote_store, issue)
                    return exporter.get_green_background_style()
                elif unicode(item['% done']) == u'0' and item['status'] == u'Rejected':
                    return exporter.get_yellow_background_style()
                else:
                    return exporter.get_default_style()
        raise Exception, 'lost task %s' % issue['#']
    
    xls = XlsExporter()
    xls.add_issues_list(planned_issues, issue_row_handler = row_handler)
    
    xls.save_to_file(export_file)
    
    logging.debug('Done')

def usage():
    print "usage: compare_report.py --query_id=QUERY_ID --start_date=START_DATE --file=FILE_TO_EXPORT"
    print "System will compare issues between START_DATE and now. For example: 2010-12-31"

if __name__ == '__main__':
    start(sys.argv[1:])