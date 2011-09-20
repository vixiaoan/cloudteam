#!/usr/bin/env python
# -*- coding:utf-8 -*-

from osv import fields,osv
import MySQLdb
import datetime
import netsvc

HOST = 'localhost'
DB = 'jjdb'
USER = 'root'
PASSWD = '1'

class customer_activity(osv.osv):
    _name = 'customer.activity'
    _discription = 'Customer Activity'
    _columns = {
        'partner_id':fields.many2one('res.partner', 'partner', required=True),
        'date':fields.date('date'),
        'point':fields.float('Point'),
        'money':fields.float('Money'),
        'pointdiff':fields.float('Pointdiff'),
        'moneydiff':fields.float('Moneydiff'),
    }

    def download_data(self, cr, uid, point=0, context=None):
        logger = netsvc.Logger()
        partner_obj = self.pool.get('res.partner')
        eta_obj = self.pool.get('email_template.account')
        etm_obj = self.pool.get('email_template.mailbox')
        user_obj = self.pool.get('res.users')

        db=MySQLdb.connect(host=HOST,db=DB,user=USER,passwd=PASSWD)
        c=db.cursor()
        c.execute("select username,money,point,pointdiff,moneydiff,postdate from point_day_log")
        results = c.fetchall()
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)
        email = {}
        body = []
        for result in results:            
            if result[5] == today - oneday:
                ids = partner_obj.search(cr, uid, [('name','=',result[0])])
                if len(ids) > 0:
                    customer_activity = {
                        'partner_id':ids[0],
                        'date':False,
                        'point':result[2] or 0.0,
                        'money':result[1] or 0.0,
                        'pointdiff':result[3] or 0.0,
                        'moneydiff':result[4] or 0.0,
                    }
                    id = self.create(cr, uid, customer_activity)
                    logger.notifyChannel('addons.'+self._name,netsvc.LOG_DEBUG,'create a customer activity log id:%s'%id)
                    partner_obj.write(cr, uid, ids, {'account_page_num':customer_activity['point'],'account_ukey_num':customer_activity['money']})
                    if customer_activity['point'] < point:
                    #generate mail body
                        body.append(str(result[0])+'|'+str(result[2])+'|'+str(result[1]))
                    print 'point:%s body:%s'%(point,body)
        if len(body)>0:
            body_text='username|point|money \n'+'\n'.join(body)
            print body_text            
        #generate mail
            eta_ids = eta_obj.search(cr, uid, [])
            if len(eta_ids) <= 0:            
                logger.notifyChannel('addons.'+self._name,netsvc.LOG_ERROR,'There is no effective email account')
                return False
            user = user_obj.browse(cr, uid, uid)
            if not user.address_id.email:
                logger.notifyChannel('addons.'+self._name,netsvc.LOG_ERROR,'There is no email for this account:%s'%user.name)
            email={
                'subject':str(today)+'[Customer Avticity]',
                'email_to':user.address_id.email,
                'body_text':body_text,
                'account_id':eta_ids[0],
            }
            print 'email:%s'%email
            etm_id = etm_obj.create(cr, uid, email)
            print 'etmid:%s'%etm_id
            etm_obj.send_this_mail(cr, uid, [etm_id])

        return True
customer_activity()
    
