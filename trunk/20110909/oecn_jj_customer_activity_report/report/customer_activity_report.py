# -*- coding:utf-8 -*-
import StringIO

from pychart import *
from report.render import render
from report.interface import report_int

class external_pdf(render):

    """ Generate External PDF """

    def __init__(self, pdf):
        render.__init__(self)
        self.pdf = pdf
        self.output_type = 'pdf'

    def _render(self):
        return self.pdf
        
class customer_activity_report(report_int):
    def create(self, cr, uid, ids, datas, context=None):
        if context is None:
            context = {}
        pdf_string = StringIO.StringIO()
        can = canvas.init(fname = pdf_string, format = 'pdf')
        data = datas['form']
        ar = area.T(
                    size = (300,200),
                    y_grid_style = None,
                    x_coord = category_coord.T(data, 0), y_range = (0, None),
                    x_axis = axis.X(label="user"),
                    y_axis = axis.Y(label="point"))
        ar.add_plot(bar_plot.T(data = data, label = "Customer Activity"))
        ar.draw(can)
        can.close()
        self.obj = external_pdf(pdf_string.getvalue())
        self.obj.render()

        pdf_string.close()
        return (self.obj.pdf, 'pdf')
        
customer_activity_report('report.customer.activity')