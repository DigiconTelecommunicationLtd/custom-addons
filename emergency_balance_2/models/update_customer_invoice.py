# -*- coding: utf-8 -*-

from odoo import models, fields, api
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
from datetime import datetime, timezone, timedelta, date

class UpdateCustomerInvoice(models.Model):
    _inherit = "account.invoice"
    require_approval = fields.Boolean(string='approval?',
                             track_visibility='onchange',default=False)
    approval_reason = fields.Char(string='reason')
    approved = fields.Boolean(string='approval?',
                                      track_visibility='onchange', default=False)

    approved_by=fields.Many2one('res.users', string='Approved By', track_visibility='onchange',default=False)

    @api.onchange('date_due')
    def date_due_thing(self):
        for record in self:
            due_date_obj = datetime.strptime(record.date_due, DEFAULT_DATE_FORMAT)
            today_new = datetime.now() + timedelta(hours=6)
            diff =abs((due_date_obj - today_new).days)
            if diff > 10:
                record.require_approval = True
            else:
                record.require_approval = False

            # modified_date_obj = due_date_obj + timedelta(days=1, hours=6)
            # record.new_next_start_date = modified_date_obj.strftime(DEFAULT_DATE_FORMAT)
            # print(record.date_due)


    @api.one
    def review_for_defer(self):
        for record in self:
            record.approved = True

