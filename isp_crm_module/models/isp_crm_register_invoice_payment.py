# -*- coding: utf-8 -*-


from odoo import api, fields, models, _

DEFAULT_DATE_FORMAT = '%Y-%m-%d'

class InvoiceRegisterPayment(models.Model):

    """Inherits account.payment"""

    _inherit = 'account.payment'

    cheque_no = fields.Char(string='Cheque No')
    cheque_date = fields.Date('Cheque Date', default=None)
    # amount = fields.Char(string='Amount')
    bank_name = fields.Char(string='Bank Name')
    branch_name = fields.Char(string='Branch Name')



