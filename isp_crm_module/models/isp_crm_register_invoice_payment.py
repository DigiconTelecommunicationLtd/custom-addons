# -*- coding: utf-8 -*-


from odoo import api, fields, models, _

DEFAULT_DATE_FORMAT = '%Y-%m-%d'

class InvoiceRegisterPayment(models.Model):

    """Inherits account.payment"""

    _inherit = 'account.payment'

    cheque_no = fields.Char(string='Cheque No')
    cheque_date = fields.Date('Cheque Date', default=None)
    bank_name = fields.Char(string='Bank Name')
    branch_name = fields.Char(string='Branch Name')
    is_dishonored = fields.Boolean(string='Is Dishonored')

    @api.multi
    def action_save(self):
        """
        Action to perform when user clicks on the save button.
        :return:
        """
        is_dishonored = self.is_dishonored
        cheque_no = self.cheque_no
        cheque_date = self.cheque_date
        bank_name = self.bank_name
        branch_name = self.branch_name

        if self.is_dishonored:
            self.update({

                'state': 'draft',
                'is_dishonored': self.is_dishonored,
                'cheque_no': self.cheque_no,
                'cheque_date': self.cheque_date,
                'bank_name': self.bank_name,
                'branch_name': self.branch_name,

            })
        else:
            self.update({

                'cheque_no': self.cheque_no,
                'cheque_date': self.cheque_date,
                'bank_name': self.bank_name,
                'branch_name': self.branch_name,

            })


