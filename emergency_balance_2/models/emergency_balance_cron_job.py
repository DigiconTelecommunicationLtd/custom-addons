# -*- coding: utf-8 -*-
import re

import base64
from odoo import models, fields, api
from odoo.exceptions import Warning, UserError
import datetime
from datetime import datetime, timezone, timedelta, date
from dateutil.relativedelta import relativedelta


DEFAULT_DATE_FORMAT = '%Y-%m-%d'

class CronJobModel(models.Model):
    _name = 'emergency_balance.cron_job'
    name = fields.Char("name", required=False)
    @api.model
    def send_defer_email(self):
        customers_list = self.env['res.partner'].search([
            ('customer', '=', True)
        ])
        for customer in customers_list:
            if customer.is_deferred:
                opportunity = self.env['crm.lead'].search([('partner_id', '=', customer.id)], limit=1)
                if opportunity:
                    if opportunity.lead_type == "retail":
                        due_date = customer.isp_invoice_id.date_due
                        customer_state = str(customer.customer_state)
                        # check if paid or not
                        print('state', customer_state)
                        if customer_state != 'False':
                            if customer_state != 'paid':
                                # check if date expired
                                print('is in paid state', 'true')
                                today_new = datetime.now() + timedelta(hours=6)
                                two_days = today_new + timedelta(days=2)

                                custom_due_date = datetime.strptime(due_date, DEFAULT_DATE_FORMAT)
                                custom_due_date = custom_due_date + timedelta(hours=6)
                                print('today', str(today_new))
                                print('due_date', str(custom_due_date))
                                print('two_days', str(two_days))
                                print('custom_due_date', str(custom_due_date.date()))
                                print('two_days', str(two_days.date()))
                                if two_days.date() == custom_due_date.date():
                                    #shoot the email
                                    print('two days and custom due same mail goint to shoot')
                                    template_obj_new_service_request = self.env[
                                        'emergency_balance.mail'].sudo().search(
                                        [('name', '=', 'new_reminder_for_deferred_mail')],
                                        limit=1)
                                    days=custom_due_date.strftime('%d, %b %Y')
                                    self.env['emergency_balance.mail'].action_send_defer_email(days,customer.name,
                                                                                               customer.subscriber_id,
                                                                                               customer.current_package_id.name,
                                                                                               str(customer.current_package_price),
                                                                                               customer.email,
                                                                                               template_obj_new_service_request
                                                                                               )
