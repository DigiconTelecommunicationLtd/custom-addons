# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
from datetime import datetime, timezone, timedelta, date
from odoo.exceptions import Warning, UserError

REQUIRE_APPROVAL = 1
APPROVED = 2
NEED_APPROVAL = 3
class UpdateCustomerInvoice(models.Model):
    _inherit = "account.invoice"
    require_approval = fields.Boolean(string='approval?',
                             track_visibility='onchange',default=False)
    approval_reason = fields.Char(string='reason')
    status = fields.Integer(default=2)
    @api.onchange('date_due')
    def date_due_thing(self):
        for record in self:
            if str(record.date_due)!= 'False':
                due_date_obj = datetime.strptime(record.date_due, DEFAULT_DATE_FORMAT)
            else:
                raise UserError(_('Please Enter a Valid Due Date!'))
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
            record.status = NEED_APPROVAL
            print(record.status)
            template_obj_new_service_request = self.env['emergency_balance.mail'].sudo().search(
                [('name', '=', 'new_reminder_for_deferred_approval_mail')],
                limit=1)

            product_name=str(record.invoice_line_ids[0].product_id.name)
            product_price =record.invoice_line_ids[0].quantity * record.invoice_line_ids[0].price_unit

            line = record.invoice_line_ids[0]
            price_subtotal = line.quantity * line.price_unit
            discount = (price_subtotal * line.discount) / 100
            price_subtotal = price_subtotal - discount

            due_date_obj = datetime.strptime(record.date_due, DEFAULT_DATE_FORMAT)
            modified_date_obj = due_date_obj + timedelta(days=1, hours=6)
            number_of_days = (modified_date_obj - datetime.now()).days


            self.env['emergency_balance.mail'].action_send_defer_review_email(str(record.name),
                                                                 record.partner_id.name,
                                                                 product_name,
                                                                 str(price_subtotal),
                                                                 str(record.approval_reason),
                                                                 str(number_of_days),
                                                                 template_obj_new_service_request
                                                                 )


    @api.one
    def approve_defer(self):
        for record in self:
            record.status = APPROVED
            print(record.status)


