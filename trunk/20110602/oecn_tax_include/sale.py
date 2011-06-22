# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
import netsvc
logger = netsvc.Logger()
class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    def create(self, cr, uid, vals, context={}):
        if 'tax_id' in vals:
            tobj = self.pool.get('account.tax')
            taxes = tobj.browse(cr, uid, vals['tax_id'][0][2])
            for t in taxes:
                if not t.price_include:
                    return super(sale_order_line, self).create(cr, uid, vals, context=context)
            tax = 0.0
            for res in tobj.compute(cr, uid, taxes, vals['price_unit'], 1):
                tax += res['amount']
            vals.update({'price_unit': vals['price_unit'] - tax})
        return super(sale_order_line, self).create(cr, uid, vals, context=context)
sale_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

