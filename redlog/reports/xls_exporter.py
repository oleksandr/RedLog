# -*- coding: utf-8 -*-
import xlwt
import logging

class XlsExporter:
    
    def __init__(self):
        self.wb = xlwt.Workbook(encoding='utf-8')
        self.ws = self.wb.add_sheet('estimation')
        
    def save_to_file(self, output_file):        
        logging.debug('Export to Excel file %s' % output_file)
        self.wb.save(output_file)
    
    def add_issues_list(self, issues, start_row = 0):
        logging.debug('Parsing issues...')
        ws = self.ws
        
        # header
        ws.write(start_row, 0, '#')
        ws.write(start_row, 1, 'status')
        ws.write(start_row, 2, 'tracker')
        ws.write(start_row, 3, 'priority')
        ws.write(start_row, 4, 'subject')
        ws.col(4).width = 0x0d00 + 10000
        
        ws.write(start_row, 5, 'assigned to')
        ws.col(5).width = 0x0d00 + 500
        
        ws.write(start_row, 6, 'estimate time')
        ws.col(6).width = 0x0d00 + 100
        
        ws.write(start_row, 7, '% done')
        ws.col(7).width = 0x0d00 + 50
                
        ws.write(start_row, 8, 'time to finish')
        ws.col(8).width = 0x0d00 + 100
        
        num_style = xlwt.easyxf('', num_format_str='#,##0.00')
        
        for issue in issues:
            for key in issue.keys():
                issue[key] = unicode(issue[key])
            
        i = start_row + 1
        for issue in issues:
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
        formula = "SUM(I%s:I%s)" % (start_row + 2, start_row + len(issues) + 1)
        ws.write(start_row + len(issues) + 1, 8, 
                 xlwt.Formula(formula))