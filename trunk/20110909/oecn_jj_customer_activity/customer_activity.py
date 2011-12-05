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

STATUS1 = u'正式客户'
STATUS2 = u'潜在客户'

class customer_activity(osv.osv):
    _name = 'customer.activity'
    _discription = 'Customer Activity'
    _columns = {
        'partner_id':fields.many2one('res.partner', 'Partner', required=True),
        'date':fields.date('Date'),
        'point':fields.float('Point'),
        'money':fields.float('Money'),
        'pointdiff':fields.float('Pointdiff'),
        'moneydiff':fields.float('Moneydiff'),
    }

    def _generate_mail(self, cr, uid, body_text='', mail_type='', mail_to =False, context={}):
        '''生成邮件，并且发送'''
        eta_obj = self.pool.get('email_template.account')
        etm_obj = self.pool.get('email_template.mailbox')
        
        today = datetime.date.today()

        eta_ids = eta_obj.search(cr, uid, [])
        if len(eta_ids) <= 0:
            #Get the email account            
            logger.notifyChannel('addons.'+self._name,netsvc.LOG_ERROR,'There is no effective email account')
            return False

        email={
            'subject':'[' + str(today.strftime('%Y-%m-%d')) + '][Customer Avticity]' + mail_type,
            'email_to':mail_to,
            'body_text':body_text,
            'account_id':eta_ids[0],
        }
            
        etm_id = etm_obj.create(cr, uid, email)
        etm_obj.send_this_mail(cr, uid, [etm_id])
        return True

    def download_data(self, cr, uid, point=0, money=0, formal_mail=[], potential_mail=[],  context=None):
        '''从网站上下载数据
           @param point:客户的point少于这个这个值
           @param money:客户的money少于这个这个值
           @param formal_mail:正式客户的数据发送到这些邮箱
           @param potential_mail：潜在客户的数据饭送到这些邮箱
        '''
        logger = netsvc.Logger()
        partner_obj = self.pool.get('res.partner')
        user_obj = self.pool.get('res.users')

        body_error_text = False
        body_text = False
        mail_type = ''
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)

        admin_user = user_obj.browse(cr, 1, 1)
        admin_email = admin_user.address_id.email
        #管理员邮箱，请务必设定!否则错误信息不能发送
        try:
            db=MySQLdb.connect(host=HOST,db=DB,user=USER,passwd=PASSWD)
        except Exception:
            logger.notifyChannel('addons.'+self._name, netsvc.LOG_ERROR,'MySQL Connect Failed.')
            body_error_text = '[Error]MySQL Connect Failed.' 
            mail_type='[ERROR]'                       
            return self._generate_mail(cr, uid, body_error_text, mail_type, admin_email, context)

        partner_ids = partner_obj.search(cr, uid, [])
        partners = partner_obj.browse(cr, uid, partner_ids)
        partner_name = []
        for partner in partners:
            partner_name.append(((partner.name).upper()).encode('utf-8'))
        
        c=db.cursor()  
        c.execute('''SELECT common_member.username,money,point,pointdiff,moneydiff,postdate \
                     FROM point_day_log \
                     LEFT JOIN common_member ON (point_day_log.uid = common_member.uid ) \
                     WHERE postdate = '%s' \
                     AND UPPER(common_member.username) IN (%s)'''%((today - oneday).strftime('%Y-%m-%d'),'"'+'","'.join(partner_name)+'"'))
        #读取Mysql数据列出前一天的网站用户的信息
        results = c.fetchall()
        email = {}
        body1 = []
        body2 = []
        if not results or len(results) <= 0:
            logger.notifyChannel('addons.'+self._name, netsvc.LOG_ERROR,'Error! There is no data get from website!')
            body_error_text = 'Warning! There is no data get from website!'
        for result in results:           
            ids = partner_obj.search(cr, uid, [('name','=',result[0])])
            if len(ids) > 0:
                customer_activity = {
                    'partner_id':ids[0],
                    'date':result[5],
                    'point':result[2] or 0.0,
                    'money':result[1] or 0.0,
                    'pointdiff':result[3] or 0.0,
                    'moneydiff':result[4] or 0.0,
                }
                id = self.create(cr, uid, customer_activity)
                logger.notifyChannel('addons.'+self._name,netsvc.LOG_DEBUG,'create a customer activity log id:%s'%id)
                partner_obj.write(cr, uid, ids, {'account_page_num':customer_activity['point'],'account_ukey_num':customer_activity['money']})
                
                #对于下载的数据进行筛选，并且分别按“正式用户”，"潜在用户"分别发邮件
                if len(formal_mail) <= 0 or len(potential_mail) <= 0:
                    #如果没设定 formal_mail 或者 potential_mail 则错误，结束流程 
                    logger.notifyChannel('addons.'+self._name,netsvc.LOG_DEBUG,'Need to setup formal_mail and potential_mail!')
                    return False
                if customer_activity['point'] < point or customer_activity['money'] < money:
                    partner = partner_obj.browse(cr, uid, ids[0])
                    
                    if partner.partner_status.name == STATUS1:
                        body1.append(str(result[0])+'|'+str(result[2])+'|'+str(result[1]))
                    if partner.partner_status.name == STATUS2:
                        body2.append(str(result[0])+'|'+str(result[2])+'|'+str(result[1]))
                
        if len(body1)>0 and len(formal_mail)>0:
            body_text='username|point|money \n'+'\n'.join(body1)
            self._generate_mail(cr, uid, body_text, mail_type+'['+STATUS1+']', ";".join(formal_mail), context)
        if len(body2)>0 and len(potential_mail)>0:
            body_text='username|point|money \n'+'\n'.join(body2)
            self._generate_mail(cr, uid, body_text, mail_type+'['+STATUS2+']', ";".join(potential_mail), context)
        if body_error_text:
            mail_type = '[ERROR]'
            self._generate_mail(cr, uid, body_error_text, mail_type, mail_to =False, context)
        return True

customer_activity()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
