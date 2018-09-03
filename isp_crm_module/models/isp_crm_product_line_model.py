# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

AVAILABLE_PRIORITIES = [
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
]



class ProductLine(models.Model):
    """
    Model for different type of Product Lines.
    """
    _name = "isp_crm_module.product_line"
    _description = "Product Lines For Service Request."
    _rec_name = 'name'
    _order = "create_date desc, name, id"

    service_request_id = fields.Many2one('isp_crm_module.service_request', string='Service Request', required=True, ondelete='cascade', index=True, copy=False)
    name = fields.Char('Request Name', required=True, index=True, copy=False, default='New')
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)],
                                 change_default=True, ondelete='restrict', required=True)
    product_updatable = fields.Boolean(compute='_compute_product_updatable', string='Can Edit Product', readonly=True,
                                       default=True)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True,
                                   default=1.0)
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    currency_id = fields.Many2one(related='service_request_id.currency_id', store=True, string='Currency', readonly=True)


    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount(self):
        """
        Compute the amounts of the Product line.
        """
        for line in self:
            price = line.price_unit * (1 / 100.0)
            line.update({
                'price_subtotal': price,
            })

    @api.depends('product_id')
    def _compute_product_updatable(self):
        for line in self:
            if line.service_request_id.is_done == False:
                line.product_updatable = True
            else:
                line.product_updatable = False