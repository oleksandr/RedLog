# -*- coding: utf-8 -*-
from redlog.models import RemoteIssuesStore, LocalStore
from redlog import settings
import xlwt
import logging
import getopt, sys
from xls_exporter import XlsExporter

logging.basicConfig(level = logging.DEBUG)

def start(argv):
    try:                          
        opts, args = getopt.getopt(argv, "", ["file=", "query_id="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
        
    if len(opts) < 2:
        usage()
        sys.exit(2)
      
    opt, arg = opts[0]
    if opt == "--query_id":
        query_id = arg
    else:
        usage()
        sys.exit(2)
    
    opt, arg = opts[1]   
    if opt == "--file":
        export_file = arg
    else:
        usage()
        sys.exit(2)
    
    logging.debug('XLS export process started (query_id = %s)' % query_id)
    
    localStore = LocalStore()
    credentials = localStore.get_credentials()
    
    if len(credentials) == 0:
        print "Can't find credentials for Redmine login. Use Redlog UI before."
        
    username = credentials[0]
    password = credentials[1]
    logging.debug('Connect to Redmine with username "%s"' % username)
    remote_store = RemoteIssuesStore(settings.REDMINE_BASE_URL, username, password)
    
    logging.debug('Getting issues...')
    issues = remote_store.get_issues_by_query_id(query_id) #41
    
    xls_exporter = XlsExporter()
    xls_exporter.add_issues_list(issues)
    xls_exporter.save_to_file(export_file)
        
    logging.debug('Done')
    
def usage():
    print "usage: export_xls.py --query_id=QUERY_ID --file=FILE_TO_EXPORT"
    print "QUERY_ID is id of saved query in Redmine. For example: 41"
    print "FILE_TO_EXPORT is full path to export file. For example: c:\export.xls"

if __name__ == '__main__':
    start(sys.argv[1:])