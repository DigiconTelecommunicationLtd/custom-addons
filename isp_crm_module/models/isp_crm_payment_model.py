# -*- coding: utf-8 -*-



from ast import literal_eval
from datetime import datetime, timedelta
from odoo import http
from odoo import api, fields, models, _
from odoo.exceptions import Warning, UserError
import odoo.addons.decimal_precision as dp

DEFAULT_BANK_ACCOUNT_CODE = '101401'
DEFAULT_UNEARNED_REVENUE_ACCOUNT_CODE = '100001'
DEFAULT_REVENUE_ACCOUNT_CODE = '111111'
DEFAULT_PAYMENT_INVOICE = 'account.payment.customer.invoice'
DEFAULT_BANK_JOURNAL_SHORTCODE = 'BNK1'

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

    customer_id = fields.Char(string="Customer ID")
    customer_name = fields.Char(string="Customer Name")
    package_name = fields.Char(string="Package Name")
    bill_start_date = fields.Char(string="Bill Start Date")
    bill_end_date = fields.Char(string="Bill End Date")
    bill_amount = fields.Char(string="Bill amount")
    received_amount = fields.Char(string="Received amount")
    deducted_amount = fields.Char(string="Deducted amount")
    bill_payment_date = fields.Char(string="Bill payment date")
    card_type = fields.Char(string="Card type")
    card_number = fields.Char(string="Card number")
    billing_status = fields.Char(string="Billing status")
    full_response = fields.Text(string="Full Response")
    bill_pay_type = fields.Char(compute="_get_bill_pay_type", string="Payment_type")

    @api.multi
    def post(self, vals={}, is_mail_sent=False):
        """
        Overrides the default post function for advance payment option
        :return:
        """
        if self.is_advance:
            self.make_advance_payment(records=self)
        else:
            super(ISPCRMPayment, self).post()

        if is_mail_sent == False:
            self.send_mail_for_payment()
        return True
    
    def _get_bill_pay_type(self):
        """
        Compute bill payment type.
        :return:
        """
        for payment in self:
            if payment.journal_id:
                payment.update({
                    'bill_pay_type': str(payment.journal_id.type),
                })


    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id:
            self.update({
                'bill_pay_type': str(self.journal_id.type),
            })

    def send_mail_for_payment(self):
        """
        Sends mail for payment
        :return: True if the payment mailing is successfull
        """
        template_obj = self.env['mail.template'].search([('name', '=', 'isp_crm_module_user_payment_mail_template')])
        for record in self:
            mail_obj = self.env['isp_crm_module.mail'].sending_mail_for_payment(payment_obj=record, template_obj=template_obj)


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

            rec.partner_id.get_customer_balance(customer_id=rec.partner_id.id)
        return True

    def customer_bill_adjustment(self, customer, package_price):
        """
        Creates new account move line to adjust the balance
        of the customer according to the given package price
        :param customer: customer Object
        :param package_price: price of the package
        :return: True if all operations are ok
        """
        # get Journal
        bank_journal_obj = self.env['account.journal'].search([('code', '=', DEFAULT_BANK_JOURNAL_SHORTCODE)], limit=1)
        # account object
        account_obj = self.env['account.account']
        # creating the move
        acc_move = self.env['account.move'].create({
            'journal_id' : bank_journal_obj.id
        })

        # account move line
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)

        # creating unearned revenue move line
        unearned_revenue_acc_obj = account_obj.search([('code', 'like', DEFAULT_UNEARNED_REVENUE_ACCOUNT_CODE)],
                                                      limit=1)
        sequence_code = DEFAULT_PAYMENT_INVOICE
        name = 'Customer Payment'
        created_unearned_revenue_move_line = aml_obj.create({
            'move_id': acc_move.id,
            'partner_id': customer.id,
            'name': name,
            'account_id': unearned_revenue_acc_obj.id,
            'debit': package_price,
        })

        # creating revenue move line
        revenue_acc_obj = account_obj.search([('code', 'like', DEFAULT_REVENUE_ACCOUNT_CODE)],
                                                      limit=1)
        sequence_code = DEFAULT_PAYMENT_INVOICE
        name = 'Customer Payment'
        created_unearned_revenue_move_line = aml_obj.create({
            'move_id': acc_move.id,
            'partner_id': customer.id,
            'name': name,
            'account_id': revenue_acc_obj.id,
            'debit': package_price,
        })
        return True

