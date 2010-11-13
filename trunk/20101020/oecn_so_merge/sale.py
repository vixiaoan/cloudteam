import time
import netsvc
from osv import fields, osv

class sale_order(osv.osv):
    _inherit = "sale.order"
    def merge(self, cr, uid, context = {}):
        wf_service = netsvc.LocalService("workflow")
        customer = context['customer_id']
        old_ids  = context['old_ids']
        # get new customer infos
        addr = self.pool.get('res.partner').address_get(cr, uid, [customer], ['delivery', 'invoice', 'contact'])
        part = self.pool.get('res.partner').browse(cr, uid, customer)
        # prepare header data
        order_data = {
            'date_order': time.strftime('%Y-%m-%d'),
            'partner_id': customer,
            'partner_order_id': addr['contact'],
            'partner_shipping_id': addr['delivery'],
            'partner_invoice_id': addr['invoice'],
            'shop_id': 0,
            'pricelist_id': part.property_product_pricelist and part.property_product_pricelist.id or False,
            'fiscal_position': part.property_account_position,
            'state': 'draft',
            'order_line': [],
        }
        
        # prepare line data
        for sorder in self.browse(cr, uid, old_ids):
                order_data.update({
                    'shop_id': sorder.shop_id.id,
                })
                old_data = self.copy_data(cr, uid, sorder.id)        
                order_data['order_line'] = order_data['order_line'] + old_data[0]['order_line'] 
               
        line_obj = self.pool.get('sale.order.line')
        for sol in order_data['order_line']:
           #empty the order_partner_id
           sol[2]['order_partner_id'] = 0
           #recalculate the price
           sol[2]['price_unit'] = self.pool.get('product.pricelist').price_get(cr, uid, [order_data['pricelist_id']],
                        sol[2]['product_id'], sol[2]['product_uom_qty'] , order_data['partner_id'], {
                            'uom': sol[2]['product_uom'],
                            'date': order_data['date_order'],
                            })[order_data['pricelist_id']]
           #get tax from customer fiscal position 
           product_obj = self.pool.get('product.product').browse(cr, uid, sol[2]['product_id'])
           sol[2]['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, order_data['fiscal_position'], product_obj.taxes_id)
           sol[2]['discount'] = 0
           sol[2]['delay'] = 0
        
        allorders = []
        order_data['fiscal_position'] = part.property_account_position.id
        # create the new order
        neworder_id = self.create(cr, uid, order_data)
        allorders.append(neworder_id)
        
        # make triggers pointing to the old orders point to the new order
        for old_id in old_ids:
            wf_service.trg_redirect(uid, 'sale.order', old_id, neworder_id, cr)
            wf_service.trg_validate(uid, 'sale.order', old_id, 'cancel', cr)
        
        return allorders
sale_order()