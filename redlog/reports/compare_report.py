# -*- coding: utf-8 -*-
from redlog.models import LocalStore, RemoteIssuesStore
import logging
import sys
from datetime import datetime
from xls_exporter import XlsExporter
from redlog import settings
from common import parameters_parse

logging.basicConfig(level = logging.DEBUG)

def start(argv):
    query_id, start_date, export_file = parameters_parse(argv, ['query_id', "start_date", 'file'], usage)
        
    localStore = LocalStore()
    logging.debug('Getting issues by query_id=%s and between %s and now' % (query_id, start_date))
    planned_issues = localStore.get_issues_by_query(query_id,
                                   start_date.strftime("%Y-%m-%d %H:%M:%S"),
                                   datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    credentials = localStore.get_credentials()
    if len(credentials) == 0:
        print "Can't find credentials for Redmine login. Use Redlog UI before."
        
    username = credentials[0]
    password = credentials[1]
    logging.debug('Connect to Redmine with username "%s"' % username)
    remote_store = RemoteIssuesStore(settings.REDMINE_BASE_URL, username, password)
    
    logging.debug('Getting issues...')
    new_issues = remote_store.get_issues_by_query_id(query_id) #41
    
    def row_handler(exporter, issue):
        # return exporter.get_default_style()
        for item in new_issues:           
            if unicode(item['#']) == unicode(issue['#']):
                issue['% done'] = item['% done']
                if unicode(item['% done']) == u'100':
                    return exporter.get_green_background_style()
                else:
                    return exporter.get_default_style()
        issue['% done'] = u'100'
        return exporter.get_green_background_style()
    
    xls = XlsExporter()
    xls.add_issues_list(planned_issues, issue_row_handler = row_handler)
    
    xls.save_to_file(export_file)
    
    logging.debug('Done')

def usage():
    print "usage: compare_report.py --query_id=QUERY_ID --start_date=START_DATE --file=FILE_TO_EXPORT"
    print "System will compare issues between START_DATE and now. For example: 2010-12-31"

if __name__ == '__main__':
    start(sys.argv[1:])