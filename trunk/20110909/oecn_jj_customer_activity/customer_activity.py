#!/usr/bin/env python
# -*- coding:utf-8 -*-

from osv import fields,osv
import MySQLdb
import datetime
import netsvc

#----mysql 配置信息----
#mysql 服务器地址
HOST = 'localhost'
#数据库名字
DB = 'jjdb'
#数据库用户名
USER = 'root'
#数据库密码
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

    def generate_mail(self, cr, uid, body_text='',mail_type='',context={} ):
        '''Generate the mail and send'''
        eta_obj = self.pool.get('email_template.account')
        etm_obj = self.pool.get('email_template.mailbox')
        user_obj = self.pool.get('res.users')

        today = datetime.date.today()

        eta_ids = eta_obj.search(cr, uid, [])
        if len(eta_ids) <= 0:
        #Get the email account            
            logger.notifyChannel('addons.'+self._name,netsvc.LOG_ERROR,'There is no effective email account')
            return False

        user = user_obj.browse(cr, uid, uid)
        if not user.address_id.email:
        #Get the email address 
            logger.notifyChannel('addons.'+self._name,netsvc.LOG_ERROR,'There is no email for this account:%s'%user.name)
            return False

        email={
            'subject':'[' + str(today) + '][Customer Avticity]' + mail_type,
            'email_to':user.address_id.email,
            'body_text':body_text,
            'account_id':eta_ids[0],
        }
            
        etm_id = etm_obj.create(cr, uid, email)
        etm_obj.send_this_mail(cr, uid, [etm_id])
        return True

    def download_data(self, cr, uid, point=0, money=0, context=None):
        '''Get the data from the website'''
        logger = netsvc.Logger()
        partner_obj = self.pool.get('res.partner')
        

        body_error_text = False
        body_text = False
        mail_type = ''
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)

        try:
            db=MySQLdb.connect(host=HOST,db=DB,user=USER,passwd=PASSWD)
        except Exception:
            logger.notifyChannel('addons.'+self._name, netsvc.LOG_ERROR,'MySQL Connect Failed.')
            body_error_text = '[Error]MySQL Connect Failed.' 
            mail_type='[ERROR]'           
            return self.generate_mail(cr, uid, body_error_text, mail_type, context)

        partner_ids = partner_obj.search(cr, uid, [])
        partners = partner_obj.browse(cr, uid, partner_ids)
        partner_name = []
        for partner in partners:
            partner_name.append(partner.name) 
        c=db.cursor()  
        c.execute('''SELECT common_member.username,money,point,pointdiff,moneydiff,postdate \
                     FROM point_day_log \
                     LEFT JOIN common_member ON (point_day_log.uid = common_member.uid ) \
                     WHERE postdate = '%s' \
                     AND common_member.username IN (%s)'''%(today - oneday,'"'+'","'.join(partner_name)+'"'))
        results = c.fetchall()
        email = {}
        body = []
        if len(results) <= 0:
            logger.notifyChannel('addons.'+self._name, netsvc.LOG_ERROR,'Error! There is no data get from website!')
            body_error_text = 'Warning! There is no data get from website!'
        for result in results:            
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
                if customer_activity['point'] < point or customer_activity['money'] < money:
                #generate mail body
                    body.append(str(result[0])+'|'+str(result[2])+'|'+str(result[1]))
                
        if len(body)>0:
            body_text='username|point|money \n'+'\n'.join(body)
        elif body_error_text:
            body_text = body_error_text
            mail_type = '[ERROR]'
        if body_text:       
            #Generate mail
            return self.generate_mail(cr, uid, body_text, mail_type, context)
        return True

customer_activity()
    
