# -*- coding: utf-8 -*-


from odoo import api, fields, models, _

class SalesOrderLine(models.Model):
    """Inherits sale.order.line and for showing order lines in service requests"""
    _inherit = 'sale.order.line'

    service_request_id = fields.Many2one('sale.order', string='Order Reference', ondelete='cascade', index=True, copy=False)
    total_price_without_vat = fields.Char(string='Total Price Without Vat')
    vat = fields.Char(string='Vat')

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_shipping_id)
            subtotal_without_vat = (taxes['total_included'] * 100.0) / 105.0
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
                'total_price_without_vat': subtotal_without_vat,
                'vat': '5.0',
            })