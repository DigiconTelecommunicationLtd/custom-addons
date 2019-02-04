# -*- coding: utf-8 -*-


from odoo import api, fields, models, _

class AccountInvoiceLine(models.Model):
    """Inherits account.invoice.line and for showing order lines in invoices"""
    _inherit = 'account.invoice.line'

    total_price_without_vat = fields.Char(string='Total Price Without Vat')
    vat = fields.Char(string='Vat')

