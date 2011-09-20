# -*- coding: utf-8 -*-

from osv import fields, osv

class customer_activity_chart_wiazrd(osv.osv_memory):
    _name = 'customer_activity_chart_wizard'
    _columns  = {
        'date_start' : fields.date('Date Start', required=True),
        'date_end' : fields.date('Date End', required=True),
        'state_id': fields.many2one("res.country.state", 'Fed. State'),
        'city': fields.char('City', size=128),
        'partner_status': fields.many2one('res.partner.status','Partner Status'),
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
        ca_obj = self.pool.get('customer.activity')
        partner_obj = self.pool.get('res.partner')
        res = self.read(cr, uid, ids, ['date_start', 'date_end','state_id','city','partner_status'], context=context)
        res = res and res[0] or {}
        if res.get('state_id',False):
            condition.append(('state_id','=',res['state_id']))
        if res.get('city',False):
            condition.append(('city','=',res['city']))
        if res.get('partner_status',False):
            condition.append(('partner_status','=',res['partner_status']))
        partner_ids = partner_obj.search(cr, uid, condition)
        cr.execute('''SELECT res_partner.name,sum(moneydiff)+sum(pointdiff) 
                        FROM customer_activity 
                        LEFT JOIN res_partner on (customer_activity.partner_id = res_partner.id)
                        WHERE partner_id in (%s)
                        GROUP BY res_partner.name'''%(",".join(map(str,partner_ids))))
        result = cr.fetchall()
        datas['form'] = result
        if res.get('id',False):
            datas['ids']=[res['id']]
        return { 'type': 'ir.actions.report.xml',
            'report_name': 'customer.activity',
            'datas': datas, }
customer_activity_chart_wiazrd()