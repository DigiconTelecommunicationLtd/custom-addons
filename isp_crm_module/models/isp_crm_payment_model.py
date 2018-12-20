# -*- coding: utf-8 -*-



from ast import literal_eval
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
import odoo.addons.decimal_precision as dp

DEFAULT_BANK_ACCOUNT_CODE = '101401'
DEFAULT_UNEARNED_REVENUE_ACCOUNT_CODE = '100001'
DEFAULT_PAYMENT_INVOICE = 'account.payment.customer.invoice'

class ISPCRMPayment(models.Model):
    """Inherits account.payment and adds Functionality in account payment"""
    _inherit = 'account.payment'


    service_type_id = fields.Many2one(
        'isp_crm_module.selfcare_payment_service',
        default=False,
        required=False,
        string='Payment Service Type'
    )
    is_advance = fields.Boolean("Is Advance", default=False)

    @api.multi
    def post(self):
        """
        Overrides the default post function for advance payment option
        :return:
        """
        if self.is_advance:
            self.make_advance_payment(records=self)
        else:
            super(ISPCRMPayment, self).post()
        return True

    def make_advance_payment(self, records):
        """
        Enlists the payments which are given in advance
        :param records: which records has to be advanced payment
        :return: True if the payment is successfull
        """
        for rec in records:
            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))
            aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
            account_obj = self.env['account.account']
            # creating the move
            acc_move = self.env['account.move'].create(self._get_move_vals())
            sequence = acc_move.journal_id.sequence_id
            acc_move.name = sequence.with_context(ir_sequence_date=acc_move.date).next_by_id()

            # creating bank move line
            bank_acc_obj = account_obj.search([('code', 'like', DEFAULT_BANK_ACCOUNT_CODE)], limit=1)
            sequence_code = DEFAULT_PAYMENT_INVOICE
            seq_name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
            name = seq_name
            created_bank_move_line = aml_obj.create({
                'move_id'       : acc_move.id,
                'partner_id'    : rec.partner_id.id,
                'name'          : name,
                'account_id'    : bank_acc_obj.id,
                'debit'         : rec.amount,
            })

            # creating unearned revenue move line
            unearned_revenue_acc_obj = account_obj.search([('code', 'like', DEFAULT_UNEARNED_REVENUE_ACCOUNT_CODE)], limit=1)
            sequence_code = DEFAULT_PAYMENT_INVOICE
            name = 'Customer Payment'
            created_unearned_revenue_move_line = aml_obj.create({
                'move_id'       : acc_move.id,
                'partner_id'    : rec.partner_id.id,
                'name'          : name,
                'account_id'    : unearned_revenue_acc_obj.id,
                'credit'        : rec.amount,
            })
            # Updating the payment object
            rec.write({
                'name' : seq_name,
                'state': 'posted',
                'move_name': acc_move.name
            })
            # updating the account.move.line
            created_bank_move_line.update({
                'payment_id': rec.id
            })
            created_unearned_revenue_move_line.update({
                'payment_id': rec.id
            })
        return True
