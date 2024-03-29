# -*- coding: utf-8 -*-

from osv import fields, osv
LIMIT = 3

class customer_activity_chart_wiazrd(osv.osv_memory):
    _name = 'customer_activity_chart_wizard'
    _columns  = {
        'date_start' : fields.date('Date Start', required=True),
        'date_end' : fields.date('Date End', required=True),
        'state_id': fields.many2one("res.country.state", 'Fed. State'),
        'city': fields.char('City', size=128),
        'partner_status': fields.many2one('res.partner.status','Partner Status'),
        'except_zero':fields.boolean('except zero?'),
    }

    
    def print_report(self, cr, uid, ids, context=None):
        """
        print the report
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param context: A standard dictionary
        @return : retrun report
        """
        if context is None:
            context = {}
        datas = {}
        condition =[]
        except_zero ='' 
        ca_obj = self.pool.get('customer.activity')
        partner_obj = self.pool.get('res.partner')
        address_obj = self.pool.get('res.partner.address')
        country_obj = self.pool.get('res.country.state')
        partner_status_obj = self.pool.get('res.partner.status')
        
        res = self.read(cr, uid, ids, ['date_start', 'date_end','state_id','city','partner_status','partner_id','except_zero'], context=context)
        res = res and res[0] or {}
        if context.get('active_model',False)=='res.partner' and context.get('active_ids',False):
            condition.append(('id','in',context['active_ids']))
        if res.get('city',False):
            condition.append(('city','=',res['city']))
        if res.get('partner_status',False):
            condition.append(('partner_status','=',res['partner_status']))
            partner_status = partner_status_obj.browse(cr, uid ,res['partner_status'])
            res['partner_status'] = partner_status.name
        partner_ids = partner_obj.search(cr, uid, condition)
        if res.get('state_id',False):
            country = country_obj.browse(cr, uid,res['state_id'])
            res['country'] = country.name
            address_ids = address_obj.search(cr, uid, [('state_id','=',res['state_id']),('partner_id','in',partner_ids)])
            partner_ids = []
            if len(address_ids)>0:
                addresss = address_obj.browse(cr, uid,address_ids)
                for address in addresss:
                    partner_ids.append(address.partner_id.id)
        if len(partner_ids)<=0:
            raise osv.except_osv(('Error!'),('The partners did not meet the conditions.'))
        if res.get('except_zero',False):
            except_zero = ' AND (moneydiff > 0 or  pointdiff > 0) '
            res['except_zero'] ='Except 0'
        cr.execute('''SELECT res_partner.name,sum(moneydiff)+sum(pointdiff) \
                        FROM customer_activity \
                        LEFT JOIN res_partner on (customer_activity.partner_id = res_partner.id)\
                        WHERE customer_activity.partner_id in (%s)  %s \
                        AND customer_activity.date<='%s' AND customer_activity.date>='%s' \
                        GROUP BY res_partner.name  \
                        ORDER BY  sum(moneydiff)+sum(pointdiff) DESC \
                        LIMIT %s'''%(",".join(map(str,partner_ids)), except_zero, res['date_end'],res['date_start'],LIMIT))
        result = cr.fetchall()
        if len(result) <= 0:
            raise osv.except_osv(('Error!'),('No Data!'))
        datas['form'] = result
        datas['condition'] = res
        print result
        if res.get('id',False):
            datas['ids']=[res['id']]
        datas['model'] = 'res.partner' 
        return { 'type': 'ir.actions.report.xml',
            'report_name': 'customer.activity',
            'datas': datas, }
customer_activity_chart_wiazrd()
