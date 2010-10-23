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
import netsvc
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

    wf_service = netsvc.LocalService("workflow")
    order_obj = pooler.get_pool(cr.dbname).get('sale.order')
    # get new customer infos
    customer = data['form']['customer']
    addr = pooler.get_pool(cr.dbname).get('res.partner').address_get(cr, uid, [customer], ['delivery', 'invoice', 'contact'])
    part = pooler.get_pool(cr.dbname).get('res.partner').browse(cr, uid, customer)

    # prepare header data
    old_ids = []
    order_data = {
        'date_order': time.strftime('%Y-%m-%d'),
        'partner_id': customer,
        'partner_order_id': addr['contact'],
        'partner_shipping_id': addr['delivery'],
        'partner_invoice_id': addr['invoice'],
        'shop_id': 0,
        'pricelist_id': part.property_product_pricelist and part.property_product_pricelist.id or False,
        'state': 'draft',
        'order_line': [],
    }

    # prepare line data
    for porder in [order for order in order_obj.browse(cr, uid, data['ids']) if order.state == 'draft']:
        old_ids.append(porder.id)
        order_data.update({
            'shop_id': porder.shop_id.id,
        })
        old_data = order_obj.copy_data(cr, uid, porder.id)

        order_data['order_line'] = order_data['order_line'] + old_data[0]['order_line'] 
    
    if len(old_ids) < 2:
        raise wizard.except_wizard(_('Error'), _('Please select at least two quota to merge'))    
    
    line_obj = pooler.get_pool(cr.dbname).get('sale.order.line')
    for sol in order_data['order_line']:
       #empty the order_partner_id
       sol[2]['order_partner_id'] = 0
       #recalculate the price
       sol[2]['price_unit'] = pooler.get_pool(cr.dbname).get('product.pricelist').price_get(cr, uid, [order_data['pricelist_id']],
                    sol[2]['product_id'], sol[2]['product_uom_qty'] , order_data['partner_id'], {
                        'uom': sol[2]['product_uom'],
                        'date': order_data['date_order'],
                        })[order_data['pricelist_id']]

    allorders = []
    # create the new order
    neworder_id = order_obj.create(cr, uid, order_data)
    allorders.append(neworder_id)

    # make triggers pointing to the old orders point to the new order
    for old_id in old_ids:
        wf_service.trg_redirect(uid, 'sale.order', old_id, neworder_id, cr)
        wf_service.trg_validate(uid, 'sale.order', old_id, 'cancel', cr)

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

