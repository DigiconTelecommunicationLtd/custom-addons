# -*- coding: utf-8 -*-


from odoo import api, fields, models, _

DEFAULT_DATE_FORMAT = '%Y-%m-%d'

class InvoiceRegisterPayment(models.Model):

    """Inherits account.payment"""

    _inherit = 'account.payment'
    _order = "create_date desc, id"

    cheque_no = fields.Char(string='Cheque No')
    cheque_date = fields.Date('Cheque Date', default=None)
    bank_name = fields.Char(string='Bank Name')
    branch_name = fields.Char(string='Branch Name')
    is_dishonored = fields.Boolean(string='Is Dishonored')
    payment_service_id = fields.Many2one('isp_crm_module.selfcare_payment_service', string='Payment Service Type',
                                         default=1)

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
        payment_service_id = self.payment_service_id

        if is_dishonored:
            self.update({

                'state': 'draft',
                'is_dishonored': is_dishonored,
                'cheque_no': cheque_no,
                'cheque_date': cheque_date,
                'bank_name': bank_name,
                'branch_name': branch_name,
                'payment_service_id': payment_service_id,

            })
        else:
            self.update({

                'cheque_no': cheque_no,
                'cheque_date': cheque_date,
                'bank_name': bank_name,
                'branch_name': branch_name,
                'payment_service_id': payment_service_id,

            })


