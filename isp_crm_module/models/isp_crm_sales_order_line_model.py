# -*- coding: utf-8 -*-


from odoo import api, fields, models, _

class SalesOrderLine(models.Model):
    """Inherits sale.order.line and for showing order lines in service requests"""
    _inherit = 'sale.order.line'

    service_request_id = fields.Many2one('sale.order', string='Order Reference', ondelete='cascade', index=True, copy=False)