# -*- coding: utf-8 -*-
from redlog.models import RemoteIssuesStore, LocalStore
import logging
import getopt, sys
from redlog import settings
from datetime import datetime

logging.basicConfig(level = logging.DEBUG)

def start(argv):
    try:                          
        opts, args = getopt.getopt(argv, "", ["query_id="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
        
    if len(opts) < 1:
        usage()
        sys.exit(2)
      
    opt, arg = opts[0]
    if opt == "--query_id":
        query_id = arg
    else:
        usage()
        sys.exit(2)
    
    logging.debug('Saving issues to local store (query_id = %s)' % query_id)
    
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
    
    logging.debug('Clear issues by query_id=%s in local store' % query_id)
    localStore.clear_issues_by_query(query_id)
    
    logging.debug('Saving new issues...')
    saved_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for issue in issues:
        localStore.save_issue_by_query(issue['#'], query_id, issue['status'], saved_datetime)
    
    logging.debug('Done')

def usage():
    print "usage: save_query_issues.py --query_id=QUERY_ID"
    print "QUERY_ID is id of saved query in Redmine. For example: 41"

if __name__ == '__main__':
    start(sys.argv[1:])
