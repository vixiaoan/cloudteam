# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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

import time

import wizard
import pooler
from osv.orm import browse_record, browse_null
from tools.translate import _

merge_form = """<?xml version="1.0"?>
<form string="Merge orders">
    <separator string="merge these orders to a new quota"/>
    <field name="customer"/>
</form>
"""

merge_fields = {
    'customer': {'string': 'New customer', 'type': 'many2one', 'relation': 'res.partner', 'required': True},    
}


def _merge_orders(self, cr, uid, data, context):

    order_obj = pooler.get_pool(cr.dbname).get('sale.order')
    # get new customer infos
    customer = data['form']['customer']
    old_ids = []
    # orders to merge
    for sorder in [order for order in order_obj.browse(cr, uid, data['ids']) if order.state == 'draft']:
        old_ids.append(sorder.id)
    if len(old_ids) < 2:
        raise wizard.except_wizard(_('Error'), _('Please select at least two quota to merge'))    
    context['customer_id'] = customer
    context['old_ids'] = old_ids
    allorders = order_obj.merge(cr, uid, context)
    return {
        'domain': "[('id','in', [" + ','.join(map(str, allorders)) + "])]",
        'name': 'Sale Orders',
        'view_type': 'form',
        'view_mode': 'tree,form',
        'res_model': 'sale.order',
        'view_id': False,
        'type': 'ir.actions.act_window'
    }


class merge_orders(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': merge_form, 'fields' : merge_fields, 'state' : [('end', 'Cancel'), ('merge', 'Merge orders') ]}
        },
        'merge': {
            'actions': [],
            'result': {'type': 'action', 'action': _merge_orders, 'state': 'end'}
        },
    }

merge_orders("oecn.sale.order.merge")

