# -*- coding: utf-8 -*-
from redlog.models import RemoteIssuesStore, LocalStore
from redlog import settings
import xlwt
import logging
import getopt, sys

logging.basicConfig(level = logging.DEBUG)

class XlsExporter:
    
    def __init__(self, issues, output_file):
        self.issues = issues
        self.output_file = output_file
    
    def export(self):
        logging.debug('Parsing issues...')
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('estimation')
        
        # header
        ws.write(0, 0, '#')
        ws.write(0, 1, 'status')
        ws.write(0, 2, 'tracker')
        ws.write(0, 3, 'priority')
        ws.write(0, 4, 'subject')
        ws.col(4).width = 0x0d00 + 10000
        
        ws.write(0, 5, 'assigned to')
        ws.col(5).width = 0x0d00 + 500
        
        ws.write(0, 6, 'estimate time')
        ws.col(6).width = 0x0d00 + 100
        
        ws.write(0, 7, '% done')
        ws.col(7).width = 0x0d00 + 50
                
        ws.write(0, 8, 'time to finish')
        ws.col(8).width = 0x0d00 + 100
        
        num_style = xlwt.easyxf('', num_format_str='#,##0.00')
        
        for issue in self.issues:
            for key in issue.keys():
                issue[key] = unicode(issue[key])
            
        i = 1
        for issue in self.issues:
            ws.write(i, 0, issue['#'])
            ws.write(i, 1, issue['status'])
            ws.write(i, 2, issue['tracker'])
            ws.write(i, 3, issue['priority'])
            ws.write(i, 4, issue['subject'])
            ws.write(i, 5, issue['assigned to'])
            ws.write(i, 6, issue['estimate time'].replace('.', ','), num_style)
            ws.write(i, 7, issue['% done'].replace('.', ','), num_style)            
            ws.write(i, 8, xlwt.Formula("G%s - G%s/100*H%s" % (i + 1, i + 1, i + 1)), num_style)
            i = i + 1
        
        # add summary
        ws.write(len(self.issues) + 1, 8, xlwt.Formula("SUM(I2:I%s)" % (len(self.issues) + 1)))
        
        logging.debug('Export to Excel file %s' % self.output_file)
        wb.save(self.output_file)

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
    
    xls_exporter = XlsExporter(issues, export_file)
    xls_exporter.export()
    
    logging.debug('Done')
    
def usage():
    print "usage: export_xls --query_id=QUERY_ID --file=FILE_TO_EXPORT"
    print "QUERY_ID is id of saved query in Redmine. For example: 41"
    print "FILE_TO_EXPORT is full path to export file. For example: c:\export.xls"

if __name__ == '__main__':
    start(sys.argv[1:])