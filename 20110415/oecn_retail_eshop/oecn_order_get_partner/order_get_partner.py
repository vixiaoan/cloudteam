from osv import osv, fields
import tools

class order_get_partner(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'
    _description = 'Using Order to Get the Partnership which does not Exist'
    
    def import_data(self, cr, uid, fields, datas, mode='init', current_module='', noupdate=False, context=None, filename=None):

        for flag in range(len(fields)):
            if fields[flag] == 'partner_id:db_id':
                dataFlag = 0
                for data in datas:
                    partner_name = data[flag]
                    partner_city = data[flag + 1] and data[flag + 1] or ''
                    partner_street = data[flag + 2] and data[flag + 2] or ''
                    partner_mobile = data[flag + 3] and data[flag + 3] or ''
                    partner_phone = data[flag + 4] and data[flag + 4] or ''
                    partner_email = data[flag + 5] and data[flag + 5] or ''
                    partner_id = None
                    contact_id = None
                    if partner_name:
                        partner_obj = self.pool.get("res.partner")
                        contact_obj = self.pool.get("res.partner.address")
                        partner_ids = partner_obj.search(cr, uid, [('name', '=', partner_name)])
                        if not partner_ids:
                            partner_id = partner_obj.create(cr, uid, {'name': partner_name, })
                            contact_id = contact_obj.create(cr, uid, {
                                'partner_id': partner_id,
                                'name': partner_name,
                                'phone': partner_phone,
                                'mobile': partner_mobile,
                                'email': partner_email,
                                'street': partner_street,
                                'city': partner_city,
                                })
                        else:
                            partner_id = partner_ids[0]
                            contact_ids = contact_obj.search(cr, uid, [('partner_id', '=', partner_id), ('street', '=', partner_street), ('city', '=', partner_city)])
                            if not contact_ids:
                                contact_id = contact_obj.create(cr, uid, {
                                    'partner_id': partner_id,
                                    'name': partner_name,
                                    'phone': partner_phone,
                                    'mobile': partner_mobile,
                                    'email': partner_email,
                                    'street': partner_street,
                                    'city': partner_city,
                                    })
                            else:
                                contact_id = contact_ids[0]
                        datas[dataFlag][flag] = partner_id
                        datas[dataFlag][flag + 1] = contact_id
                        dataFlag += 1

        return super(order_get_partner, self).import_data(cr, uid, fields, datas, mode, current_module, noupdate, context, filename)

order_get_partner()
