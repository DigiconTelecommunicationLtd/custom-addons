# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from datetime import datetime, timezone, timedelta, date
from odoo.addons.emergency_balance_2.models.color_code import *
DEFAULT_DATE_FORMAT = '%Y-%m-%d'

class updated_res(models.Model):
    _inherit = 'res.partner'

    emergency_date = fields.Integer(string='Emergency Balance', help="Emergency Balance")
    emergency_balance_due_amount =  fields.Float('Due Amount', required=True,
                                          default=0.0,
                                          track_visibility='onchange')
    emergency_due_date = fields.Date(string='Emergency Valid Till',default=False,track_visibility='onchange')
    has_due = fields.Boolean(string='due?',
                            track_visibility='onchange')

    new_next_start_date =fields.Date(string="New Start Date", compute='_compute_new_start_date')
    isp_invoice_id = fields.Many2one('account.invoice', string='Invoice',ondelete='restrict', track_visibility='onchange',default=False)
    customer_balance = fields.Char(string='Balance',compute='_compute_customer_balance')
    customer_state = fields.Char(compute='_compute_state', string="State")
    amount_total_signed = fields.Float(compute='_compute_state', string="Invoiced Amount")
    customer_total_due = fields.Float(compute='_compute_due', string="Due")

    @api.one
    def _compute_due(self):
        total_due = 0.0
        for record in self:
        #     if record.is_deferred and str(record.customer_state)!='paid':
        #         total_due = record.amount_total_signed
        #         print('total_sign',str(total_due))
        #     if record.has_due:
        #         today_new = datetime.now() + timedelta(hours=6)
        #         custom_valid_till = datetime.strptime(record.new_next_start_date, DEFAULT_DATE_FORMAT)
        #         if today_new > custom_valid_till:
        #             total_due = record.emergency_balance_due_amount
        #         print('total_sign', str(total_due))
        # print('total_sign', str(total_due))
            if record.has_due:
                today_new = datetime.now() + timedelta(hours=6)
                custom_valid_till = datetime.strptime(record.new_next_start_date, DEFAULT_DATE_FORMAT)
                if today_new > custom_valid_till:
                    total_due = record.emergency_balance_due_amount
            else:
                total_due = str(0.0)

        self.customer_total_due = total_due

    @api.one
    def _compute_state(self):
        for record in self:
            record.customer_state=str(self.isp_invoice_id.state)
            print(str(self.isp_invoice_id.amount_total_signed))
            record.amount_total_signed = self.isp_invoice_id.amount_total_signed


    @api.one
    def _compute_new_start_date(self):
        for record in self:
            if record.has_due:
                due_date_obj = datetime.strptime(record.emergency_due_date, DEFAULT_DATE_FORMAT)
                modified_date_obj=due_date_obj + timedelta(hours=6)
                record.new_next_start_date = modified_date_obj.strftime(DEFAULT_DATE_FORMAT)
            else:
                record.new_next_start_date = record.current_package_end_date

    @api.one
    def _compute_customer_balance(self):
        balance="{0:.2f}".format(abs(self.env['res.partner'].get_customer_balance(self.id)))
        self.customer_balance = balance
        # for record in self:
        #     print(record)
        #     record.customer_balance=str(abs(record.get_customer_balance(record.subscriber_id)))


    @api.one
    def update_emergency_balance(self):
        for record in self:
            record.has_due = False
            record.emergency_due_date = False
            record.emergency_balance_due_amount = 0.0
            record.emergency_date = 0
            data = self.env['emergency.balance'].sudo().search(
                [('customer', '=', self.id), ('has_due', '=', 'true')], limit=1)

            data.has_due = False
            data.set_for_approval = False
            data.approved = False
            data.rejected = False
            data.due_paid = True
            data.state = 'paid'
            data.color=DUE_PAID
