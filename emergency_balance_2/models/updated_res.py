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
    customer_balance = fields.Char(string='Balance',compute='_compute_customer_balance')

    @api.one
    def _compute_new_start_date(self):
        for record in self:
            if record.has_due:
                due_date_obj = datetime.strptime(record.emergency_due_date, DEFAULT_DATE_FORMAT)
                modified_date_obj=due_date_obj + timedelta(days=1,hours=6)
                record.new_next_start_date=modified_date_obj.strftime(DEFAULT_DATE_FORMAT)
            else:
                record.new_next_start_date = record.current_package_end_date

    @api.one
    def _compute_customer_balance(self):
        for record in self:
            record.customer_balance=str(abs(record.get_customer_balance(str(self.subscriber_id))))


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
