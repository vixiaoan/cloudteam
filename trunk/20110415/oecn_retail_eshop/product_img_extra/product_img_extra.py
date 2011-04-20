from osv import osv, fields
import urllib2
import base64
class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    _description = 'Product'

    def _get_image(self, cursor, user, ids, name, arg, context=None):
        image = {}
        opener = urllib2.build_opener()
        res = self.read(cursor, user, ids, ['image_link'])
        imageLink = res[0]['image_link']
        pic = base64.encodestring(opener.open(imageLink).read())
        for id in ids:
            image[id] = pic
        return image

    _columns = {
        'image_link' : fields.text('ImageLink'), 
        'image' : fields.function(_get_image, method=True, string='Product Image', type='binary', store=True), 
    }

product_product()
