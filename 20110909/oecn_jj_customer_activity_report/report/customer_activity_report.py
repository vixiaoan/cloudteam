# -*- coding:utf-8 -*-

from addons.pxgo_openoffice_reports.openoffice_report import openoffice_report,OOReport
        
class customer_activity_report(OOReport):

    def get_report_context(self):
        res = super(customer_activity_report, self).get_report_context()
        res.update({
             'lines':self.data['form'],
             'condition':self.data['condition']
        })
       # print 'lines:%s'%res['lines']

        return res


openoffice_report('report.customer.activity','res.partner',parser=customer_activity_report)
