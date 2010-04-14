# -*- coding: utf-8 -*-
from redlog.models import RemoteIssuesStore
from redlog import settings
import xlwt

class XlsExporter:
    
    def __init__(self, issues, output_file):
        self.issues = issues
        self.output_file = output_file
    
    def export(self):
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
        
        wb.save(self.output_file)

def start():
    remote_store = RemoteIssuesStore(settings.REDMINE_BASE_URL, 'username', 'password')
    issues = remote_store.get_issues_by_query_id(41)
    xls_exporter = XlsExporter(issues, "c:\\export.xls")
    xls_exporter.export()

if __name__ == '__main__':
    start()