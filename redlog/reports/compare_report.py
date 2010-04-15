# -*- coding: utf-8 -*-
from redlog.models import LocalStore
import logging
import getopt, sys
from datetime import datetime

logging.basicConfig(level = logging.DEBUG)

def start(argv):
    try:                          
        opts, args = getopt.getopt(argv, "", ["query_id=", "start_date="])
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
    if opt == "--start_date":
        start_date = datetime.strptime(arg, "%Y-%m-%d")
    else:
        usage()
        sys.exit(2)
        
    localStore = LocalStore()
    logging.debug('Getting issues by query_id=%s and between %s and now' % (query_id, start_date))
    planned_issues = localStore.get_issues_by_query(query_id,
                                   start_date.strftime("%Y-%m-%d %H:%M:%S"),
                                   datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def usage():
    print "usage: compare_report.py --query_id=QUERY_ID --start_date=START_DATE"
    print "System will compare issues between START_DATE and now. For example: 2010-12-31"

if __name__ == '__main__':
    start(sys.argv[1:])