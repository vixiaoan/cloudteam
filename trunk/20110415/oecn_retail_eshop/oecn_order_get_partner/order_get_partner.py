from osv import osv, fields
import tools

class order_get_partner(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'
    _description = 'Using Order to Get the Partnership which does not Exist'
    
    def import_data(self, cr, uid, fields, datas, mode='init', current_module='', noupdate=False, context=None, filename=None):

        for flag in range(len(fields)):
            if fields[flag] == 'note':
                for data in datas:
                    note = data[flag]
                    if note and note.split("|"):
                        partner_map = {}
                        parameters = note.split("|")
                        for parameter in parameters:
                            partner_map[parameter.split(':')[0]] = parameter.split(':')[1]
                        if partner_map['name']:
                            partner_obj = self.pool.get("res.partner")
                            contact_obj = self.pool.get("res.partner.address")
                            partner_id = partner_obj.search(cr, uid, [('name', '=', partner_map['name'])])
                            if not partner_id:
                                partner_id = partner_obj.create(cr, uid, {'name': partner_map['name'],})
                                if partner_map.__len__() > 1:
                                    contact_id = contact_obj.create(cr, uid, {
                                        'partner_id': partner_id,
                                        'name': partner_map['name'],
                                        'phone': partner_map.has_key('phone') and partner_map['phone'] or '',
                                        'mobile': partner_map.has_key('mobile') and partner_map['mobile'] or '',
                                        'email': partner_map.has_key('email') and partner_map['email'] or '',
                                        'street': partner_map.has_key('street') and partner_map['street'] or '',
                                        'city': partner_map.has_key('city') and partner_map['city'] or '',
                                    })

        return super(order_get_partner, self).import_data(cr, uid, fields, datas, mode, current_module, noupdate, context, filename)

order_get_partner()