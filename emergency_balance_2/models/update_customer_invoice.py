# -*- coding: utf-8 -*-

from odoo import models, fields, api
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
from datetime import datetime, timezone, timedelta, date
REQUIRE_APPROVAL = 1
APPROVED = 2
class UpdateCustomerInvoice(models.Model):
    _inherit = "account.invoice"
    require_approval = fields.Boolean(string='approval?',
                             track_visibility='onchange',default=False)
    approval_reason = fields.Char(string='reason')
    status = fields.Integer(default=2)
    @api.onchange('date_due')
    def date_due_thing(self):
        for record in self:
            due_date_obj = datetime.strptime(record.date_due, DEFAULT_DATE_FORMAT)
            today_new = datetime.now() + timedelta(hours=6)
            #diff =abs((due_date_obj - today_new).days)
            diff =(due_date_obj - today_new).days
            diff = diff + 1
            if diff > 10:
               record.status = REQUIRE_APPROVAL
            else:
                record.status = APPROVED

            print(today_new)
            print (due_date_obj)
            print(str(record.status))
            # modified_date_obj = due_date_obj + timedelta(days=1, hours=6)
            # record.new_next_start_date = modified_date_obj.strftime(DEFAULT_DATE_FORMAT)
            # print(record.date_due)


    @api.one
    def review_for_defer(self):
        for record in self:
            record.status = APPROVED

    @api.onchange('payment_term_id', 'date_invoice')
    def _onchange_payment_term_date_invoice(self):
        print('********************')
        date_invoice = self.date_invoice
        print('date_invoice before if ',date_invoice)
        if not date_invoice:
            date_invoice = fields.Date.context_today(self)
            print('date_invoice after if ', date_invoice)

        print('self.payment_term_id', self.payment_term_id)
        if self.payment_term_id:
            pterm = self.payment_term_id
            pterm_list = \
            pterm.with_context(currency_id=self.company_id.currency_id.id).compute(value=1, date_ref=date_invoice)[0]
            self.date_due = max(line[0] for line in pterm_list)
            print('self.date_due', self.date_due)
        elif self.date_due and (date_invoice > self.date_due):
            self.date_due = date_invoice
            print('self.date_due2', self.date_due)
