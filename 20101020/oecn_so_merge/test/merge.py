import xmlrpclib
DB = 'l10n'
USERID = 1
USERPASS = 'admin'


sock = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/object' % ('localhost',8069))

ids = sock.execute(DB, USERID, USERPASS, 'sale.order', 'search', [('state','=','draft')])

print ids

context = {}

context['customer_id'] = 1
context['old_ids'] = ids

new_order = sock.execute(DB, USERID, USERPASS, 'sale.order', 'merge', context)

print new_order
