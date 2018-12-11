# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp

class CustomerPackageHistory(models.Model):
    """Saves the customer Package history"""
    _name = 'isp_crm_module.customer_package_history'
    _description = "Customer Package history"
    _order = "create_date desc, name, id"

    name = fields.Char("Name", default='', required=False)
    customer_id = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)],
                               track_visibility='onchange')
    package_id = fields.Many2one('product.product', string='Package', domain=[('sale_ok', '=', True)],
                                      change_default=True, ondelete='restrict')
    start_date = fields.Date('Package Start Date', default=None)
    end_date = fields.Date('Package End Date', default=None)
    price = fields.Float("Package's Price", required=True,
                                      digits=dp.get_precision('Product Price'), default=0.0)
    original_price = fields.Float("Package's Original Price", required=True,
                                               digits=dp.get_precision('Product Price'), default=0.0)
