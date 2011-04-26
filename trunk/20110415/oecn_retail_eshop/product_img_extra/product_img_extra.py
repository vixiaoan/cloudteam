from osv import osv, fields
import urllib2
import base64
class product_template_img(osv.osv):
    _name = 'product.template'
    _inherit = 'product.template'
    _description = 'Product Extra Image'

    def _get_image(self, cursor, user, ids, name, arg, context=None):
        image = {}
        opener = urllib2.build_opener()
        res = self.read(cursor, user, ids, ['image_link'])
        image_link = res[0]['image_link']
        if image_link:
            pic = base64.encodestring(opener.open(image_link).read())
            for id in ids:
                image[id] = pic
        return image

    _columns = {
        'image_link' : fields.char('ImageLink', size=180),
        'image' : fields.function(_get_image, method=True, string='Product Image', type='binary', store=False), 
    }

product_template_img()
