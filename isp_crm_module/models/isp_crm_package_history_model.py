# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import Warning, UserError
import odoo.addons.decimal_precision as dp

import datetime

class PackageHistory(models.Model):
    """
    Model for showing the Package change History.
    """
    _name = "isp_crm_module.package_history"
    _description = "Package Change History of a customer."
    _order = "create_date desc, id"
    _rec_name = 'name'

    name = fields.Char('Name', required=False, index=True, copy=False, default='New')
    customer_id = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)])
    package_id = fields.Many2one('product.product', string='Package', domain=[('sale_ok', '=', True)],
                                         change_default=True, ondelete='restrict')
    start_date = fields.Date('Package Start Date', default=None)
    end_date = fields.Date('Package End Date', default=None)
    price = fields.Float('Package Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    original_price = fields.Float('Package Original Price', digits=dp.get_precision('Product Price'), default=0.0)